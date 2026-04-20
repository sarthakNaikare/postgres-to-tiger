const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://postgres-to-tiger-production.up.railway.app';

export interface BenchmarkRequest {
  table_name: string;
  timestamp_column: string;
  value_columns: string[];
  rows_per_day: number;
  query_range_days: number;
  benchmark_days: number;
}

export interface DBResult {
  ingest_duration_seconds: number;
  ingest_rate_rows_per_sec: number;
  avg_query_latency_ms: number;
  p95_query_latency_ms: number;
  storage_size: string;
  total_rows: number;
}

export interface BenchmarkResponse {
  session_id: string;
  mode: string;
  postgres: DBResult;
  timescale: DBResult;
  verdict: {
    ingest_improvement: string;
    latency_improvement: string;
    recommend_migration: boolean;
  };
  workload_summary: {
    total_rows: number;
    total_queries: number;
  };
  migration_sql: string;
}

export async function runBenchmark(request: BenchmarkRequest): Promise<BenchmarkResponse> {
  const response = await fetch(`${API_URL}/benchmark`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Benchmark failed');
  }

  return response.json();
}

export async function getStatus(sessionId: string) {
  const response = await fetch(`${API_URL}/status/${sessionId}`);
  return response.json();
}
