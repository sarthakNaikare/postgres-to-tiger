from pydantic import BaseModel, Field
from typing import List, Optional


class BenchmarkRequest(BaseModel):
    """
    What the user sends us.
    All fields are validated automatically by FastAPI.
    """
    table_name: str = Field(
        ...,
        description="Name of the table to benchmark",
        example="sensor_readings"
    )
    timestamp_column: str = Field(
        ...,
        description="Name of the timestamp column",
        example="recorded_at"
    )
    value_columns: List[str] = Field(
        ...,
        description="List of numeric columns to benchmark",
        example=["temperature", "humidity", "pressure"]
    )
    rows_per_day: int = Field(
        default=10000,
        ge=1000,       # minimum 1000 rows/day
        le=100000,     # maximum 100000 rows/day — safety limit
        description="How many rows per day your workload inserts"
    )
    query_range_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="How many days back your typical query looks"
    )
    benchmark_days: int = Field(
        default=7,
        ge=3,
        le=14,
        description="How many days of data to simulate"
    )


class DBResult(BaseModel):
    """Results for one database."""
    ingest_duration_seconds: float
    ingest_rate_rows_per_sec: float
    avg_query_latency_ms: float
    p95_query_latency_ms: float
    storage_size: str
    total_rows: int


class Verdict(BaseModel):
    """The recommendation."""
    ingest_improvement: str
    latency_improvement: str
    recommend_migration: bool


class BenchmarkResponse(BaseModel):
    """What we send back to the user."""
    session_id: str
    postgres: DBResult
    timescale: DBResult
    verdict: Verdict
    workload_summary: dict
    migration_sql: Optional[str] = None
