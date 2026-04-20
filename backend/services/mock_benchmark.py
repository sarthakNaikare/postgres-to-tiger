import random
import uuid
from services.workload_generator import WorkloadConfig
from services.sql_generator import generate_migration_sql


def run_mock_benchmark(config: WorkloadConfig) -> dict:
    """
    Returns realistic simulated benchmark results.
    Used when Docker-in-Docker is not available (e.g. Railway deployment).
    Results are based on real benchmarks run locally during development.
    """

    total_rows = config.rows_per_day * config.benchmark_days

    # Postgres baseline — scales linearly with row count
    pg_ingest_rate = round(random.uniform(25000, 32000), 2)
    pg_ingest_duration = round(total_rows / pg_ingest_rate, 2)
    pg_avg_latency = round(random.uniform(35, 65) * (total_rows / 70000), 2)
    pg_p95_latency = round(pg_avg_latency * random.uniform(1.4, 1.8), 2)
    pg_storage_kb = round(total_rows * 0.051)  # ~51 bytes per row

    # TimescaleDB — better query latency at scale, slower ingest
    ts_ingest_rate = round(random.uniform(1600, 2200), 2)
    ts_ingest_duration = round(total_rows / ts_ingest_rate, 2)
    ts_avg_latency = round(pg_avg_latency * random.uniform(0.65, 0.85), 2)
    ts_p95_latency = round(ts_avg_latency * random.uniform(1.3, 1.6), 2)
    ts_storage_kb = round(pg_storage_kb * random.uniform(0.85, 1.1))

    ingest_improvement = round(ts_ingest_rate / pg_ingest_rate, 2)
    latency_improvement = round(pg_avg_latency / ts_avg_latency, 2)

    migration_sql = generate_migration_sql(config)

    return {
        "session_id": str(uuid.uuid4())[:8],
        "mode": "demo",
        "postgres": {
            "ingest_duration_seconds": pg_ingest_duration,
            "ingest_rate_rows_per_sec": pg_ingest_rate,
            "avg_query_latency_ms": pg_avg_latency,
            "p95_query_latency_ms": pg_p95_latency,
            "storage_size": f"{pg_storage_kb} kB",
            "total_rows": total_rows
        },
        "timescale": {
            "ingest_duration_seconds": ts_ingest_duration,
            "ingest_rate_rows_per_sec": ts_ingest_rate,
            "avg_query_latency_ms": ts_avg_latency,
            "p95_query_latency_ms": ts_p95_latency,
            "storage_size": f"{ts_storage_kb} kB",
            "total_rows": total_rows
        },
        "verdict": {
            "ingest_improvement": f"{ingest_improvement}x",
            "latency_improvement": f"{latency_improvement}x",
            "recommend_migration": latency_improvement > 1.15 and total_rows >= 10000
        },
        "workload_summary": {
            "total_rows": total_rows,
            "total_queries": 10
        },
        "migration_sql": migration_sql
    }
