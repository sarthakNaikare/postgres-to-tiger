from services.container_manager import create_session_containers, destroy_session_containers
from services.workload_generator import WorkloadConfig
from services.benchmark_runner import run_full_benchmark
import json

config = WorkloadConfig(
    table_name="sensor_readings",
    timestamp_column="recorded_at",
    value_columns=["temperature", "humidity"],
    rows_per_day=15000,
    query_range_days=7,
    benchmark_days=7
)

print("Spinning up containers...")
session = create_session_containers()

try:
    results = run_full_benchmark(session, config)
    print("\n=== BENCHMARK RESULTS ===")
    print(json.dumps(results, indent=2))
finally:
    print("\nDestroying containers...")
    destroy_session_containers(session)
    print("Done.")
