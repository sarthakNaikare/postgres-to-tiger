from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re


class BenchmarkRequest(BaseModel):
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
        example=["temperature", "humidity"]
    )
    rows_per_day: int = Field(
        default=10000,
        ge=1000,
        le=100000,
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

    @validator("table_name")
    def table_name_must_be_valid(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("table_name cannot be empty")
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError(
                "table_name must start with a letter or underscore "
                "and contain only letters, numbers, underscores"
            )
        return v.lower()

    @validator("timestamp_column")
    def timestamp_column_must_be_valid(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("timestamp_column cannot be empty")
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError(
                "timestamp_column must contain only letters, numbers, underscores"
            )
        return v.lower()

    @validator("value_columns")
    def value_columns_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("value_columns must have at least one column")
        if len(v) > 10:
            raise ValueError("value_columns cannot have more than 10 columns")
        cleaned = []
        for col in v:
            col = col.strip()
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', col):
                raise ValueError(
                    f"Column name '{col}' is invalid — use only letters, numbers, underscores"
                )
            cleaned.append(col.lower())
        return cleaned


class DBResult(BaseModel):
    ingest_duration_seconds: float
    ingest_rate_rows_per_sec: float
    avg_query_latency_ms: float
    p95_query_latency_ms: float
    storage_size: str
    total_rows: int


class Verdict(BaseModel):
    ingest_improvement: str
    latency_improvement: str
    recommend_migration: bool


class BenchmarkResponse(BaseModel):
    session_id: str
    postgres: DBResult
    timescale: DBResult
    verdict: Verdict
    workload_summary: dict
    migration_sql: Optional[str] = None
