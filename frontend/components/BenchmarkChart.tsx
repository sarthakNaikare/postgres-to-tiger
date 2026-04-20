'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { BenchmarkResponse } from '@/lib/api';

export default function BenchmarkChart({ results }: { results: BenchmarkResponse }) {
  const latencyData = [
    {
      name: 'Avg Latency (ms)',
      Postgres: results.postgres.avg_query_latency_ms,
      TimescaleDB: results.timescale.avg_query_latency_ms,
    },
    {
      name: 'p95 Latency (ms)',
      Postgres: results.postgres.p95_query_latency_ms,
      TimescaleDB: results.timescale.p95_query_latency_ms,
    },
  ];

  const ingestData = [
    {
      name: 'Ingest Rate (rows/sec)',
      Postgres: results.postgres.ingest_rate_rows_per_sec,
      TimescaleDB: results.timescale.ingest_rate_rows_per_sec,
    },
  ];

  return (
    <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800">
      <h3 className="text-lg font-semibold mb-8 text-gray-200">Benchmark Results</h3>

      <div className="grid grid-cols-2 gap-4 mb-8">
        {[
          { label: 'Postgres Ingest', value: `${results.postgres.ingest_rate_rows_per_sec.toLocaleString()} rows/sec` },
          { label: 'TimescaleDB Ingest', value: `${results.timescale.ingest_rate_rows_per_sec.toLocaleString()} rows/sec` },
          { label: 'Postgres Avg Latency', value: `${results.postgres.avg_query_latency_ms} ms` },
          { label: 'TimescaleDB Avg Latency', value: `${results.timescale.avg_query_latency_ms} ms` },
          { label: 'Postgres Storage', value: results.postgres.storage_size },
          { label: 'TimescaleDB Storage', value: results.timescale.storage_size },
        ].map((stat) => (
          <div key={stat.label} className="bg-gray-800 rounded-xl p-4">
            <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
            <p className="text-lg font-semibold text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="mb-8">
        <h4 className="text-sm text-gray-400 mb-4">Query Latency — lower is better</h4>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={latencyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            <Bar dataKey="Postgres" fill="#6b7280" radius={[4, 4, 0, 0]} />
            <Bar dataKey="TimescaleDB" fill="#f97316" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h4 className="text-sm text-gray-400 mb-4">Ingest Rate — higher is better</h4>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={ingestData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#f3f4f6' }}
            />
            <Legend />
            <Bar dataKey="Postgres" fill="#6b7280" radius={[4, 4, 0, 0]} />
            <Bar dataKey="TimescaleDB" fill="#f97316" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
