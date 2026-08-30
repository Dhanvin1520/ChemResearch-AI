import { useState, useEffect } from 'react';
import type { GraphStats } from '../types';
import { api } from '../api/client';

export default function GraphDashboard() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await api.getGraphStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to Knowledge Graph');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading-spinner"><span className="spinner"></span> Connecting to graph database...</div>;
  if (error) return <div className="error-message">{error}</div>;

  if (!stats?.connected) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="2"></circle>
            <circle cx="19" cy="5" r="2"></circle>
            <circle cx="5" cy="5" r="2"></circle>
            <circle cx="5" cy="19" r="2"></circle>
            <circle cx="19" cy="19" r="2"></circle>
            <line x1="12" y1="14" x2="5" y2="17"></line>
            <line x1="12" y1="14" x2="19" y2="17"></line>
            <line x1="12" y1="10" x2="5" y2="7"></line>
            <line x1="12" y1="10" x2="19" y2="7"></line>
          </svg>
        </div>
        <div className="empty-state-text">Knowledge Graph Disconnected</div>
        <div className="empty-state-subtext">Ensure the database is running and configured correctly.</div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="section-title mb-1">Knowledge Graph</h2>
          <div className="text-sm text-secondary">
            Connected to graph database
          </div>
        </div>
        <button className="btn btn-secondary" onClick={loadStats}>Refresh Stats</button>
      </div>

      <div className="metrics-grid mb-3">
        <div className="metric-card">
          <div className="metric-value">{Object.values(stats.node_counts).reduce((a, b) => a + b, 0)}</div>
          <div className="metric-label">Total Nodes</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{Object.values(stats.relationship_counts).reduce((a, b) => a + b, 0)}</div>
          <div className="metric-label">Total Relationships</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Node Distribution</h3>
        </div>
        <div style={{ display: 'grid', gap: '0.5rem' }}>
          {Object.entries(stats.node_counts).map(([label, count]) => (
            <div key={label} className="flex justify-between items-center" style={{ padding: '0.6rem 0.85rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
              <div className="flex items-center gap-1">
                <span className={`tag ${label === 'Molecule' || label === 'Catalyst' || label === 'Solvent' ? 'entity' : label === 'Reaction' ? 'reaction' : ''}`}>
                  {label}
                </span>
              </div>
              <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 600 }}>{count}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card mt-2">
        <div className="card-header">
          <h3 className="card-title">Relationship Distribution</h3>
        </div>
        <div style={{ display: 'grid', gap: '0.5rem' }}>
          {Object.entries(stats.relationship_counts).map(([type, count]) => (
            <div key={type} className="flex justify-between items-center" style={{ padding: '0.6rem 0.85rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)' }}>
              <div className="text-sm text-secondary font-mono">{type}</div>
              <div className="font-mono" style={{ fontSize: '0.85rem', fontWeight: 600 }}>{count}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
