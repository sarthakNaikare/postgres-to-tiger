'use client';

import { useState } from 'react';
import { runBenchmark, BenchmarkRequest, BenchmarkResponse } from '@/lib/api';
import BenchmarkChart from '@/components/BenchmarkChart';
import MigrationSQL from '@/components/MigrationSQL';

const DEFAULT_FORM: BenchmarkRequest = {
  table_name: 'sensor_readings',
  timestamp_column: 'recorded_at',
  value_columns: ['temperature', 'humidity', 'pressure'],
  rows_per_day: 10000,
  query_range_days: 7,
  benchmark_days: 7,
};

export default function Home() {
  const [form, setForm] = useState<BenchmarkRequest>(DEFAULT_FORM);
  const [valueColumnsInput, setValueColumnsInput] = useState('temperature, humidity, pressure');
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('');
  const [results, setResults] = useState<BenchmarkResponse | null>(null);
  const [error, setError] = useState('');

  const stages = [
    'Spinning up containers...',
    'Benchmarking vanilla Postgres...',
    'Benchmarking TimescaleDB...',
    'Calculating results...',
  ];

  async function handleSubmit() {
    setLoading(true);
    setResults(null);
    setError('');

    const parsedColumns = valueColumnsInput
      .split(',')
      .map(c => c.trim())
      .filter(Boolean);

    const request = { ...form, value_columns: parsedColumns };

    let stageIndex = 0;
    setStage(stages[0]);
    const stageTimer = setInterval(() => {
      stageIndex = Math.min(stageIndex + 1, stages.length - 1);
      setStage(stages[stageIndex]);
    }, 2500);

    try {
      const data = await runBenchmark(request);
      setResults(data);
    } catch (err: any) {
      setError(typeof err.message === 'string' ? err.message : JSON.stringify(err));
    } finally {
      clearInterval(stageTimer);
      setLoading(false);
      setStage('');
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 text-white">
      <div className="border-b border-gray-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">Postgres <span className="text-orange-400">to</span> Tiger</h1>
            <p className="text-xs text-gray-400">Live migration benchmark playground</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold mb-3">
            Should you migrate to <span className="text-orange-400">TimescaleDB</span>?
          </h2>
          <p className="text-gray-400 text-lg">
            Paste your schema. Get real benchmarks. Make an informed decision.
          </p>
        </div>

        <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 mb-8">
          <h3 className="text-lg font-semibold mb-6 text-gray-200">Your Schema</h3>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Table Name</label>
              <input
                type="text"
                value={form.table_name}
                onChange={e => setForm({ ...form, table_name: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
                placeholder="sensor_readings"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Timestamp Column</label>
              <input
                type="text"
                value={form.timestamp_column}
                onChange={e => setForm({ ...form, timestamp_column: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
                placeholder="recorded_at"
              />
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm text-gray-400 mb-2">Value Columns (comma separated)</label>
            <input
              type="text"
              value={valueColumnsInput}
              onChange={e => setValueColumnsInput(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
              placeholder="temperature, humidity, pressure"
            />
          </div>

          <div className="grid grid-cols-3 gap-6 mb-8">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Rows per Day</label>
              <input
                type="text" inputMode="numeric"
                value={form.rows_per_day}
                onChange={e => setForm({ ...form, rows_per_day: parseInt(e.target.value) || 0 })}
                onBlur={e => setForm(f => ({ ...f, rows_per_day: Math.min(500000, Math.max(100, f.rows_per_day || 10000)) }))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Query Range (days)</label>
              <input
                type="text" inputMode="numeric"
                value={form.query_range_days}
                onChange={e => setForm({ ...form, query_range_days: parseInt(e.target.value) || 0 })}
                onBlur={e => setForm(f => ({ ...f, query_range_days: Math.min(60, Math.max(1, f.query_range_days || 7)) }))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Benchmark Days</label>
              <input
                type="text" inputMode="numeric"
                value={form.benchmark_days}
                onChange={e => setForm({ ...form, benchmark_days: parseInt(e.target.value) || 0 })}
                onBlur={e => setForm(f => ({ ...f, benchmark_days: Math.min(30, Math.max(1, f.benchmark_days || 7)) }))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-orange-400"
              />
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-orange-500 hover:bg-orange-400 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? stage : 'Run Benchmark'}
          </button>

          {error && (
            <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
          )}
        </div>

        {results && (
          <div className="space-y-8">
            <div className={`rounded-2xl p-6 border ${results.verdict.recommend_migration ? 'bg-green-950 border-green-800' : 'bg-gray-900 border-gray-800'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold mb-1">
                    {results.verdict.recommend_migration ? 'Migration Recommended' : 'Migration Not Recommended Yet'}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    {results.verdict.recommend_migration
                      ? 'TimescaleDB shows meaningful performance gains for your workload.'
                      : 'At this scale, vanilla Postgres performs comparably. Consider migrating when your data grows.'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-orange-400">{results.verdict.latency_improvement}</p>
                  <p className="text-xs text-gray-400">query speedup</p>
                </div>
              </div>
            </div>

            <BenchmarkChart results={results} />
            <MigrationSQL sql={results.migration_sql} />

            {results.mode === 'demo' && (
              <p className="text-center text-xs text-gray-600">
                Results are simulated based on real benchmarks. Deploy locally with Docker for live measurements.
              </p>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
