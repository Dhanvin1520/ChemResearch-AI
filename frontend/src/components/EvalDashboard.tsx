import { useState, useEffect } from 'react';
import type { EvaluationResults } from '../types';
import { api } from '../api/client';

export default function EvalDashboard() {
  const [results, setResults] = useState<EvaluationResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {
    try {
      setLoading(true);
      const data = await api.getEvaluationResults();
      if ((data as any).message) {
         setResults(null);
      } else {
         setResults(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  const runEval = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.runEvaluation();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed');
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, metricKey, isPercentage = true }: { title: string, metricKey: string, isPercentage?: boolean }) => {
    const data = results?.metrics[metricKey];
    if (!data) return null;

    const value = isPercentage ? `${(data.mean * 100).toFixed(1)}%` : data.mean.toFixed(2);
    const range = isPercentage
      ? `${(data.min * 100).toFixed(0)}% - ${(data.max * 100).toFixed(0)}%`
      : `${data.min.toFixed(2)} - ${data.max.toFixed(2)}`;

    return (
      <div className="metric-card slide-up">
        <div className="metric-value">{value}</div>
        <div className="metric-label">{title}</div>
        <div className="metric-range">Range: {range}</div>
      </div>
    );
  };

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="section-title mb-1">System Evaluation</h2>
          {results && (
            <div className="text-sm text-secondary">
              Processed {results.total_questions} queries in {results.total_time_seconds}s ({results.avg_time_per_question_ms}ms avg)
            </div>
          )}
        </div>
        <button className="btn btn-primary" onClick={runEval} disabled={loading}>
          {loading ? 'Running Benchmark...' : 'Run Full Benchmark'}
        </button>
      </div>

      {error && <div className="error-message mb-3">{error}</div>}

      {!results && !loading && (
         <div className="empty-state">
           <div className="empty-state-icon">
             <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
               <line x1="18" y1="20" x2="18" y2="10"></line>
               <line x1="12" y1="20" x2="12" y2="4"></line>
               <line x1="6" y1="20" x2="6" y2="14"></line>
             </svg>
           </div>
           <div className="empty-state-text">No evaluation data</div>
           <div className="empty-state-subtext">Run a benchmark to evaluate the system against the 50-question dataset</div>
         </div>
      )}

      {results && (
        <>
          <h3 className="section-title mt-3 mb-2">Entity Extraction Precision</h3>
          <div className="metrics-grid">
            <MetricCard title="Catalyst Extraction (F1)" metricKey="catalyst_f1" />
            <MetricCard title="Solvent Extraction (F1)" metricKey="solvent_f1" />
            <MetricCard title="Molecule Extraction (F1)" metricKey="molecule_f1" />
            <MetricCard title="Reaction Extraction (F1)" metricKey="reaction_f1" />
          </div>

          <h3 className="section-title mt-3 mb-2">Answer Quality</h3>
          <div className="metrics-grid">
            <MetricCard title="Citation Support Score" metricKey="citation_score" />
            <MetricCard title="Citation Accuracy" metricKey="citation_accuracy" />
            <MetricCard title="Evidence Count" metricKey="evidence_count" isPercentage={false} />
            <MetricCard title="Answer Generation Rate" metricKey="has_answer" />
          </div>
        </>
      )}
    </div>
  );
}
