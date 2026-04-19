from services.workload_generator import WorkloadConfig, build_workload

# Simulate a user who has a sensor readings table
config = WorkloadConfig(
    table_name="sensor_readings",
    timestamp_column="recorded_at",
    value_columns=["temperature", "humidity", "pressure"],
    rows_per_day=1000,
    query_range_days=7
)

workload = build_workload(config)

print("=== CREATE TABLE ===")
print(workload["create_table"])

print(f"\n=== INSERTS (showing first 3 of {workload['total_rows']}) ===")
for insert in workload["inserts"][:3]:
    print(insert)

print(f"\n=== QUERIES (showing first 1 of {workload['total_queries']}) ===")
print(workload["queries"][0])

print(f"\nTotal rows to insert: {workload['total_rows']}")
print(f"Total queries to run: {workload['total_queries']}")
