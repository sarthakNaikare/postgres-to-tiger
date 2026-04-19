from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import BenchmarkRequest, BenchmarkResponse
from services.container_manager import create_session_containers, destroy_session_containers
from services.workload_generator import WorkloadConfig
from services.benchmark_runner import run_full_benchmark
from services.sql_generator import generate_migration_sql

router = APIRouter()


@router.post("/benchmark", response_model=BenchmarkResponse)
async def run_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint. Accepts a schema description, runs benchmark,
    returns results. Containers are always destroyed after — even on error.
    """

    # Build workload config from user request
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
        raise HTTPException(
            status_code=503,
            detail=f"Could not start benchmark containers: {str(e)}"
        )

    # Run benchmark — always destroy containers after, even if it crashes
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
        # This runs no matter what — success or failure
        # We use background_tasks so the response is sent first,
        # then containers are cleaned up
        background_tasks.add_task(destroy_session_containers, session)
