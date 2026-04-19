from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import BenchmarkRequest, BenchmarkResponse
from services.workload_generator import WorkloadConfig
from services.sql_generator import generate_migration_sql
from services.mock_benchmark import run_mock_benchmark
from utils.session_store import create_session, update_session, complete_session, fail_session
import threading
import os

router = APIRouter()

MAX_CONCURRENT_SESSIONS = 3
active_sessions = 0
sessions_lock = threading.Lock()

# Set DEMO_MODE=true in environment to use mock results
# On Railway this is true. On Oracle Cloud with Docker it's false.
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"


@router.post("/benchmark")
async def run_benchmark(request: BenchmarkRequest, background_tasks: BackgroundTasks):
    global active_sessions

    with sessions_lock:
        if active_sessions >= MAX_CONCURRENT_SESSIONS:
            raise HTTPException(
                status_code=429,
                detail="Server is busy — max 3 concurrent benchmarks. Try again in a minute."
            )
        active_sessions += 1

    config = WorkloadConfig(
        table_name=request.table_name,
        timestamp_column=request.timestamp_column,
        value_columns=request.value_columns,
        rows_per_day=request.rows_per_day,
        query_range_days=request.query_range_days,
        benchmark_days=request.benchmark_days
    )

    try:
        if DEMO_MODE:
            # Simulate progress delay so frontend polling works naturally
            import asyncio
            session_id = __import__('uuid').uuid4().hex[:8]
            create_session(session_id)

            update_session(session_id, "Spinning up containers...", 10)
            await asyncio.sleep(2)

            update_session(session_id, "Benchmarking vanilla Postgres...", 35)
            await asyncio.sleep(3)

            update_session(session_id, "Benchmarking TimescaleDB...", 65)
            await asyncio.sleep(3)

            update_session(session_id, "Calculating results...", 90)
            await asyncio.sleep(1)

            results = run_mock_benchmark(config)
            results["session_id"] = session_id
            complete_session(session_id)
            return results

        else:
            # Real Docker benchmark
            from services.container_manager import create_session_containers, destroy_session_containers
            from services.benchmark_runner import run_full_benchmark

            try:
                session = create_session_containers()
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not start benchmark containers: {str(e)}"
                )

            session_id = session["session_id"]
            create_session(session_id)

            try:
                results = run_full_benchmark(session, config)
                migration_sql = generate_migration_sql(config)
                results["migration_sql"] = migration_sql
                complete_session(session_id)
                return results

            except Exception as e:
                fail_session(session_id, str(e))
                raise HTTPException(
                    status_code=500,
                    detail=f"Benchmark failed: {str(e)}"
                )

            finally:
                background_tasks.add_task(destroy_session_containers, session)

    finally:
        with sessions_lock:
            active_sessions -= 1
