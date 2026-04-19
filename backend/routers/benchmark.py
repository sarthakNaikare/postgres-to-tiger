from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import BenchmarkRequest, BenchmarkResponse
from services.container_manager import create_session_containers, destroy_session_containers
from services.workload_generator import WorkloadConfig
from services.benchmark_runner import run_full_benchmark
from services.sql_generator import generate_migration_sql
import threading

router = APIRouter()

# Concurrency control — max 3 sessions at once
MAX_CONCURRENT_SESSIONS = 3
active_sessions = 0
sessions_lock = threading.Lock()


@router.post("/benchmark", response_model=BenchmarkResponse)
async def run_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    global active_sessions

    # Check concurrency limit
    with sessions_lock:
        if active_sessions >= MAX_CONCURRENT_SESSIONS:
            raise HTTPException(
                status_code=429,
                detail="Server is busy — max 3 concurrent benchmarks. Try again in a minute."
            )
        active_sessions += 1

    # Build workload config
    config = WorkloadConfig(
        table_name=request.table_name,
        timestamp_column=request.timestamp_column,
        value_columns=request.value_columns,
        rows_per_day=request.rows_per_day,
        query_range_days=request.query_range_days,
        benchmark_days=request.benchmark_days
    )

    # Spin up containers
    try:
        session = create_session_containers()
    except Exception as e:
        with sessions_lock:
            active_sessions -= 1
        raise HTTPException(
            status_code=503,
            detail=f"Could not start benchmark containers: {str(e)}"
        )

    # Run benchmark
    try:
        results = run_full_benchmark(session, config)
        migration_sql = generate_migration_sql(config)
        results["migration_sql"] = migration_sql
        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark failed: {str(e)}"
        )

    finally:
        # Always decrement counter and destroy containers
        with sessions_lock:
            active_sessions -= 1
        background_tasks.add_task(destroy_session_containers, session)
