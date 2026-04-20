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
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<BenchmarkResponse | null>(null);
  const [error, setError] = useState('');

  const stages = [
    { label: 'Spinning up containers...', pct: 15 },
    { label: 'Benchmarking vanilla Postgres...', pct: 40 },
    { label: 'Benchmarking TimescaleDB...', pct: 70 },
    { label: 'Calculating results...', pct: 90 },
  ];

  async function handleSubmit() {
    setLoading(true);
    setResults(null);
    setError('');
    setProgress(0);

    const parsedColumns = valueColumnsInput.split(',').map(c => c.trim()).filter(Boolean);
    const request = { ...form, value_columns: parsedColumns };

    let stageIndex = 0;
    setStage(stages[0].label);
    setProgress(stages[0].pct);

    const stageTimer = setInterval(() => {
      stageIndex = Math.min(stageIndex + 1, stages.length - 1);
      setStage(stages[stageIndex].label);
      setProgress(stages[stageIndex].pct);
    }, 2500);

    try {
      const data = await runBenchmark(request);
      setResults(data);
      setProgress(100);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Check your inputs and try again.');
    } finally {
      clearInterval(stageTimer);
      setLoading(false);
      setStage('');
    }
  }

  return (
    <main style={{
      minHeight: '100vh',
      background: '#080c14',
      color: '#e8eaf0',
      fontFamily: "'DM Sans', 'IBM Plex Sans', system-ui, sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        .hero-grid {
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(rgba(255,90,0,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,90,0,0.03) 1px, transparent 1px);
          background-size: 60px 60px;
          pointer-events: none;
        }

        .glow-orb {
          position: absolute;
          width: 600px;
          height: 600px;
          background: radial-gradient(circle, rgba(255,90,0,0.08) 0%, transparent 70%);
          top: -100px;
          right: -100px;
          pointer-events: none;
        }

        .input-field {
          width: 100%;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 10px;
          padding: 12px 16px;
          color: #e8eaf0;
          font-size: 14px;
          font-family: 'DM Mono', monospace;
          outline: none;
          transition: border-color 0.2s, background 0.2s;
        }

        .input-field:focus {
          border-color: #ff5a00;
          background: rgba(255,90,0,0.05);
        }

        .label {
          display: block;
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #6b7280;
          margin-bottom: 8px;
        }

        .btn-primary {
          width: 100%;
          background: linear-gradient(135deg, #ff5a00, #ff8c00);
          border: none;
          border-radius: 12px;
          padding: 16px;
          color: white;
          font-size: 15px;
          font-weight: 700;
          font-family: 'DM Sans', sans-serif;
          letter-spacing: 0.02em;
          cursor: pointer;
          transition: all 0.2s;
          position: relative;
          overflow: hidden;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 8px 30px rgba(255,90,0,0.4);
        }

        .btn-primary:disabled {
          background: linear-gradient(135deg, #2a2a2a, #333);
          cursor: not-allowed;
        }

        .progress-bar {
          height: 3px;
          background: rgba(255,255,255,0.06);
          border-radius: 2px;
          margin-top: 12px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #ff5a00, #ff8c00);
          border-radius: 2px;
          transition: width 0.8s ease;
        }

        .card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 16px;
          padding: 32px;
        }

        .stat-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 12px;
          padding: 20px;
          transition: border-color 0.2s;
        }

        .stat-card:hover {
          border-color: rgba(255,90,0,0.3);
        }

        .verdict-recommended {
          background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.03));
          border: 1px solid rgba(34,197,94,0.2);
          border-radius: 16px;
          padding: 28px 32px;
        }

        .verdict-not-recommended {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.1);
          border-radius: 16px;
          padding: 28px 32px;
        }

        .badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: rgba(255,90,0,0.1);
          border: 1px solid rgba(255,90,0,0.2);
          border-radius: 20px;
          padding: 4px 12px;
          font-size: 11px;
          font-weight: 600;
          color: #ff8c00;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }

        .section-title {
          font-size: 11px;
          font-weight: 700;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: #4b5563;
          margin-bottom: 20px;
        }

        .nav-link {
          color: #6b7280;
          text-decoration: none;
          font-size: 13px;
          font-weight: 500;
          transition: color 0.2s;
        }

        .nav-link:hover { color: #e8eaf0; }

        .tiger-logo {
          font-size: 20px;
          font-weight: 800;
          letter-spacing: -0.02em;
          color: white;
        }

        .tiger-logo span {
          color: #ff5a00;
        }

        .divider {
          height: 1px;
          background: rgba(255,255,255,0.06);
          margin: 8px 0;
        }

        .mono { font-family: 'DM Mono', monospace; }

        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }

        .loading-dot {
          display: inline-block;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #ff5a00;
          animation: pulse-dot 1s ease-in-out infinite;
          margin-right: 8px;
        }
      `}</style>

      {/* Background effects */}
      <div className="hero-grid" />
      <div className="glow-orb" />

      {/* Nav */}
      <nav style={{
        position: 'relative',
        zIndex: 10,
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        padding: '0 32px',
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxWidth: '1100px',
        margin: '0 auto',
      }}>
        <div className="tiger-logo">
          postgres <span>→</span> tiger
        </div>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <span className="badge">Demo Mode</span>
          <a href="https://github.com/sarthakNaikare/postgres-to-tiger" className="nav-link" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://www.timescale.com" className="nav-link" target="_blank" rel="noreferrer">
            TimescaleDB
          </a>
        </div>
      </nav>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '60px 32px' }}>

        {/* Hero */}
        <div style={{ textAlign: 'center', marginBottom: '64px', position: 'relative' }}>
          <div style={{ marginBottom: '16px' }}>
            <span className="badge">🐯 Tiger Data Migration Tool</span>
          </div>
          <h1 style={{
            fontSize: 'clamp(36px, 5vw, 58px)',
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: '-0.03em',
            marginBottom: '20px',
            background: 'linear-gradient(135deg, #ffffff 40%, #ff8c00)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Should you migrate<br />to TimescaleDB?
          </h1>
          <p style={{
            fontSize: '18px',
            color: '#6b7280',
            maxWidth: '520px',
            margin: '0 auto',
            lineHeight: 1.6,
          }}>
            Paste your schema. Run real benchmarks. Get honest results — including when migration isn't worth it yet.
          </p>

          {/* Stats row */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '40px',
            marginTop: '40px',
            flexWrap: 'wrap',
          }}>
            {[
              { value: '< 60s', label: 'per benchmark' },
              { value: '3', label: 'metrics measured' },
              { value: '100%', label: 'honest results' },
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '28px', fontWeight: 800, color: '#ff5a00', letterSpacing: '-0.02em' }}>{stat.value}</div>
                <div style={{ fontSize: '12px', color: '#4b5563', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="card" style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
            <div>
              <p className="section-title">Your Schema</p>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#e8eaf0' }}>Configure your benchmark</h2>
            </div>
            <div style={{
              padding: '8px 16px',
              background: 'rgba(255,90,0,0.08)',
              border: '1px solid rgba(255,90,0,0.15)',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#ff8c00',
              fontFamily: 'DM Mono, monospace',
            }}>
              POST /benchmark
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div>
              <label className="label">Table Name</label>
              <input
                className="input-field"
                type="text"
                value={form.table_name}
                onChange={e => setForm({ ...form, table_name: e.target.value })}
                placeholder="sensor_readings"
              />
            </div>
            <div>
              <label className="label">Timestamp Column</label>
              <input
                className="input-field"
                type="text"
                value={form.timestamp_column}
                onChange={e => setForm({ ...form, timestamp_column: e.target.value })}
                placeholder="recorded_at"
              />
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label className="label">Value Columns <span style={{ color: '#374151', textTransform: 'none', letterSpacing: 0 }}>(comma separated)</span></label>
            <input
              className="input-field"
              type="text"
              value={valueColumnsInput}
              onChange={e => setValueColumnsInput(e.target.value)}
              placeholder="temperature, humidity, pressure"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '28px' }}>
            <div>
              <label className="label">Rows / Day</label>
              <input
                className="input-field"
                type="text"
                inputMode="numeric"
                value={form.rows_per_day || ''}
                onChange={e => setForm({ ...form, rows_per_day: parseInt(e.target.value) || 0 })}
                onBlur={() => setForm(f => ({ ...f, rows_per_day: Math.min(500000, Math.max(100, f.rows_per_day || 10000)) }))}
                placeholder="10000"
              />
            </div>
            <div>
              <label className="label">Query Range (days)</label>
              <input
                className="input-field"
                type="text"
                inputMode="numeric"
                value={form.query_range_days || ''}
                onChange={e => setForm({ ...form, query_range_days: parseInt(e.target.value) || 0 })}
                onBlur={() => setForm(f => ({ ...f, query_range_days: Math.min(60, Math.max(1, f.query_range_days || 7)) }))}
                placeholder="7"
              />
            </div>
            <div>
              <label className="label">Benchmark Days</label>
              <input
                className="input-field"
                type="text"
                inputMode="numeric"
                value={form.benchmark_days || ''}
                onChange={e => setForm({ ...form, benchmark_days: parseInt(e.target.value) || 0 })}
                onBlur={() => setForm(f => ({ ...f, benchmark_days: Math.min(30, Math.max(1, f.benchmark_days || 7)) }))}
                placeholder="7"
              />
            </div>
          </div>

          <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <span className="loading-dot" />
                {stage}
              </span>
            ) : 'Run Benchmark →'}
          </button>

          {loading && (
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: progress + '%' }} />
            </div>
          )}

          {error && (
            <div style={{
              marginTop: '16px',
              padding: '12px 16px',
              background: 'rgba(239,68,68,0.08)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: '8px',
              color: '#f87171',
              fontSize: '13px',
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {results && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

            {/* Verdict */}
            <div className={results.verdict.recommend_migration ? 'verdict-recommended' : 'verdict-not-recommended'}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '20px' }}>{results.verdict.recommend_migration ? '✅' : '⚖️'}</span>
                    <h3 style={{ fontSize: '20px', fontWeight: 700, color: results.verdict.recommend_migration ? '#4ade80' : '#e8eaf0' }}>
                      {results.verdict.recommend_migration ? 'Migration Recommended' : 'Not Recommended Yet'}
                    </h3>
                  </div>
                  <p style={{ color: '#6b7280', fontSize: '14px', lineHeight: 1.6, maxWidth: '480px' }}>
                    {results.verdict.recommend_migration
                      ? 'TimescaleDB shows meaningful performance gains for your workload. Time to migrate.'
                      : 'At this scale, vanilla Postgres performs comparably. Consider migrating when your data grows beyond 10k rows/day.'}
                  </p>
                </div>
                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontSize: '48px', fontWeight: 800, color: '#ff5a00', letterSpacing: '-0.03em', lineHeight: 1 }}>
                    {results.verdict.latency_improvement}
                  </div>
                  <div style={{ fontSize: '12px', color: '#4b5563', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    query speedup
                  </div>
                </div>
              </div>
            </div>

            {/* Charts */}
            <BenchmarkChart results={results} />

            {/* Migration SQL */}
            <MigrationSQL sql={results.migration_sql ?? ''} />

            {/* Demo notice */}
            {results.mode === 'demo' && (
              <p style={{ textAlign: 'center', fontSize: '12px', color: '#374151' }}>
                Results are simulated based on real benchmarks run locally. Deploy with Docker for live measurements.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid rgba(255,255,255,0.06)',
        padding: '32px',
        marginTop: '80px',
        textAlign: 'center',
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ fontSize: '13px', color: '#374151' }}>
            Built by <a href="https://github.com/sarthakNaikare" style={{ color: '#ff8c00', textDecoration: 'none' }}>Sarthak Naikare</a> for Tiger Data
          </div>
          <div style={{ display: 'flex', gap: '24px' }}>
            <a href="https://github.com/sarthakNaikare/postgres-to-tiger" style={{ fontSize: '12px', color: '#374151', textDecoration: 'none' }} target="_blank" rel="noreferrer">Source Code</a>
            <a href="https://postgres-to-tiger-production.up.railway.app/docs" style={{ fontSize: '12px', color: '#374151', textDecoration: 'none' }} target="_blank" rel="noreferrer">API Docs</a>
            <a href="https://www.timescale.com" style={{ fontSize: '12px', color: '#374151', textDecoration: 'none' }} target="_blank" rel="noreferrer">TimescaleDB</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
