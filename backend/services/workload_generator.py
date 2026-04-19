import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class WorkloadConfig:
    """
    Everything we need to know about the user's workload.
    This gets built from the form the user fills out.
    """
    table_name: str
    timestamp_column: str
    value_columns: List[str]        # Names of the numeric columns
    rows_per_day: int               # How many rows the user inserts per day
    query_range_days: int           # How far back their queries look
    benchmark_days: int = 7         # How many days of data we simulate (fixed at 7 for speed)


def generate_create_table_sql(config: WorkloadConfig) -> str:
    """
    Generates the CREATE TABLE statement for both containers.
    Both get identical tables — fair comparison.
    """
    columns = [f"{config.timestamp_column} TIMESTAMPTZ NOT NULL"]

    for col in config.value_columns:
        columns.append(f"{col} DOUBLE PRECISION")

    columns_sql = ",\n    ".join(columns)

    return f"""
CREATE TABLE IF NOT EXISTS {config.table_name} (
    {columns_sql}
);
""".strip()


def generate_insert_statements(config: WorkloadConfig) -> List[str]:
    """
    Generates INSERT statements covering benchmark_days worth of data.
    Total rows = rows_per_day * benchmark_days
    """
    inserts = []
    now = datetime.utcnow()
    total_rows = config.rows_per_day * config.benchmark_days

    for i in range(total_rows):
        # Spread timestamps evenly across the benchmark period
        offset_seconds = int((config.benchmark_days * 24 * 3600) * i / total_rows)
        ts = now - timedelta(seconds=offset_seconds)
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

        # Generate random realistic values for each column
        values = [f"'{ts_str}'"]
        for _ in config.value_columns:
            values.append(str(round(random.uniform(0.0, 100.0), 4)))

        values_sql = ", ".join(values)
        col_names = ", ".join([config.timestamp_column] + config.value_columns)

        inserts.append(
            f"INSERT INTO {config.table_name} ({col_names}) VALUES ({values_sql});"
        )

    return inserts


def generate_select_queries(config: WorkloadConfig) -> List[str]:
    """
    Generates 10 realistic range queries.
    These are the queries we'll time on both databases.
    """
    queries = []
    now = datetime.utcnow()

    for _ in range(10):
        # Random end point within our benchmark data
        end = now - timedelta(days=random.randint(0, config.benchmark_days - 1))
        start = end - timedelta(days=config.query_range_days)

        start_str = start.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end.strftime("%Y-%m-%d %H:%M:%S")

        # Pick a random value column to aggregate
        col = random.choice(config.value_columns)

        queries.append(f"""
SELECT
    date_trunc('hour', {config.timestamp_column}) AS bucket,
    AVG({col}) AS avg_{col},
    MIN({col}) AS min_{col},
    MAX({col}) AS max_{col}
FROM {config.table_name}
WHERE {config.timestamp_column} BETWEEN '{start_str}' AND '{end_str}'
GROUP BY bucket
ORDER BY bucket;
""".strip())

    return queries


def build_workload(config: WorkloadConfig) -> dict:
    """
    Master function — builds everything needed for the benchmark.
    Returns a dict with create table SQL, inserts, and queries.
    """
    return {
        "create_table": generate_create_table_sql(config),
        "inserts": generate_insert_statements(config),
        "queries": generate_select_queries(config),
        "total_rows": config.rows_per_day * config.benchmark_days,
        "total_queries": 10
    }
