from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.schemas import BenchmarkRequest, BenchmarkResponse
from services.container_manager import create_session_containers, destroy_session_containers
from services.workload_generator import WorkloadConfig
from services.benchmark_runner import run_full_benchmark
from services.sql_generator import generate_migration_sql
from utils.session_store import create_session, update_session, complete_session, fail_session
import threading

router = APIRouter()

MAX_CONCURRENT_SESSIONS = 3
active_sessions = 0
sessions_lock = threading.Lock()


@router.post("/benchmark", response_model=BenchmarkResponse)
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

    # Start tracking this session
    try:
        update_session("pending", "Spinning up containers...", 5)
        session = create_session_containers()
    except Exception as e:
        with sessions_lock:
            active_sessions -= 1
        raise HTTPException(
            status_code=503,
            detail=f"Could not start benchmark containers: {str(e)}"
        )

    session_id = session["session_id"]

    # Register session in store
    create_session(session_id)
    update_session(session_id, "Containers ready. Starting benchmark...", 10)

    try:
        update_session(session_id, "Benchmarking vanilla Postgres...", 25)
        results = run_full_benchmark_with_progress(session, config, session_id)

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
        with sessions_lock:
            active_sessions -= 1
        background_tasks.add_task(destroy_session_containers, session)


def run_full_benchmark_with_progress(session, config, session_id):
    """
    Thin wrapper around run_full_benchmark that updates progress
    at each stage so the frontend can show live status.
    """
    from services.workload_generator import build_workload
    from services.benchmark_runner import run_benchmark_on_single_db

    update_session(session_id, "Building workload...", 15)
    workload = build_workload(config)

    update_session(session_id, "Benchmarking vanilla Postgres...", 30)
    pg_results = run_benchmark_on_single_db(
        session["postgres"],
        workload,
        is_timescale=False
    )

    update_session(session_id, "Benchmarking TimescaleDB...", 60)
    ts_results = run_benchmark_on_single_db(
        session["timescale"],
        workload,
        is_timescale=True
    )

    update_session(session_id, "Calculating results...", 90)

    from services.benchmark_runner import extract_table_name
    ingest_improvement = round(
        ts_results["ingest_rate_rows_per_sec"] / pg_results["ingest_rate_rows_per_sec"], 2
    )
    latency_improvement = round(
        pg_results["avg_query_latency_ms"] / ts_results["avg_query_latency_ms"], 2
    )

    return {
        "session_id": session["session_id"],
        "postgres": pg_results,
        "timescale": ts_results,
        "verdict": {
            "ingest_improvement": f"{ingest_improvement}x",
            "latency_improvement": f"{latency_improvement}x",
            "recommend_migration": latency_improvement > 1.2 or ingest_improvement > 1.2
        },
        "workload_summary": {
            "total_rows": workload["total_rows"],
            "total_queries": workload["total_queries"]
        }
    }
