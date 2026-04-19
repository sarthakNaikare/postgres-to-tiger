import psycopg2
import time
from typing import Dict
from services.workload_generator import WorkloadConfig, build_workload


def get_connection(conn_info: dict):
    return psycopg2.connect(
        host=conn_info["host"],
        port=conn_info["port"],
        user=conn_info["user"],
        password=conn_info["password"],
        dbname=conn_info["dbname"]
    )


def get_storage_size(cur, table_name: str, is_timescale: bool) -> str:
    if is_timescale:
        cur.execute(f"SELECT pg_size_pretty(hypertable_size('{table_name}'));")
    else:
        cur.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table_name}'));")
    return cur.fetchone()[0]


def run_benchmark_on_single_db(conn_info: dict, workload: dict, is_timescale: bool = False) -> dict:
    conn = get_connection(conn_info)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(workload["create_table"])

    if is_timescale:
        table_name = extract_table_name(workload["create_table"])
        timestamp_col = extract_timestamp_col(workload["create_table"])
        try:
            cur.execute(f"""
                SELECT create_hypertable('{table_name}', '{timestamp_col}',
                if_not_exists => TRUE);
            """)
        except Exception as e:
            print(f"Hypertable creation note: {e}")

    ingest_start = time.time()
    inserts = workload["inserts"]
    batch_size = 500

    for i in range(0, len(inserts), batch_size):
        batch = inserts[i:i + batch_size]
        cur.execute("\n".join(batch))

    ingest_duration = time.time() - ingest_start
    total_rows = workload["total_rows"]
    ingest_rate = round(total_rows / ingest_duration, 2)

    query_times = []
    for query in workload["queries"]:
        q_start = time.time()
        cur.execute(query)
        cur.fetchall()
        query_times.append((time.time() - q_start) * 1000)

    avg_latency_ms = round(sum(query_times) / len(query_times), 2)
    p95_latency_ms = round(sorted(query_times)[int(len(query_times) * 0.95)], 2)

    table_name = extract_table_name(workload["create_table"])
    storage_size = get_storage_size(cur, table_name, is_timescale)

    cur.close()
    conn.close()

    return {
        "ingest_duration_seconds": round(ingest_duration, 2),
        "ingest_rate_rows_per_sec": ingest_rate,
        "avg_query_latency_ms": avg_latency_ms,
        "p95_query_latency_ms": p95_latency_ms,
        "storage_size": storage_size,
        "total_rows": total_rows
    }


def extract_table_name(create_sql: str) -> str:
    words = create_sql.upper().split()
    idx = words.index("TABLE")
    next_word = words[idx + 1]
    if next_word == "IF":
        return create_sql.split()[idx + 4].split("(")[0].lower()
    return create_sql.split()[idx + 1].split("(")[0].lower()


def extract_timestamp_col(create_sql: str) -> str:
    for line in create_sql.split("\n"):
        if "TIMESTAMPTZ" in line.upper():
            return line.strip().split()[0].lower()
    raise ValueError("No TIMESTAMPTZ column found in schema")


def run_full_benchmark(session_info: dict, config: WorkloadConfig) -> dict:
    print("Building workload...")
    workload = build_workload(config)

    print("Benchmarking vanilla Postgres...")
    pg_results = run_benchmark_on_single_db(
        session_info["postgres"],
        workload,
        is_timescale=False
    )

    print("Benchmarking TimescaleDB...")
    ts_results = run_benchmark_on_single_db(
        session_info["timescale"],
        workload,
        is_timescale=True
    )

    ingest_improvement = round(
        ts_results["ingest_rate_rows_per_sec"] / pg_results["ingest_rate_rows_per_sec"], 2
    )
    latency_improvement = round(
        pg_results["avg_query_latency_ms"] / ts_results["avg_query_latency_ms"], 2
    )

    return {
        "session_id": session_info["session_id"],
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
