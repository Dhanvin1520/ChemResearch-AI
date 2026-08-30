import type { SearchResponse } from '../types';

interface AnswerCardProps {
  result: SearchResponse;
}

export default function AnswerCard({ result }: AnswerCardProps) {
  const scoreClass = result.citation_score >= 0.8 ? 'high' : result.citation_score >= 0.5 ? 'medium' : 'low';

  return (
    <div className="answer-card slide-up">
      <div className="answer-header">
        <h3>Research Answer</h3>
        <div className={`citation-score ${scoreClass}`}>
          Citation Support: {(result.citation_score * 100).toFixed(0)}%
        </div>
      </div>

      <div className="answer-body">{result.answer}</div>

      <div className="answer-meta">
        <div className="meta-item">
          <span className="meta-label">Claims:</span>
          <span className="meta-value">{result.supported_claims}/{result.total_claims}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Sources:</span>
          <span className="meta-value">{result.citations.length}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Evidence:</span>
          <span className="meta-value">{result.evidence.length}</span>
        </div>
        <div className="meta-item">
          <span className="meta-label">Time:</span>
          <span className="meta-value">{result.processing_time_ms}ms</span>
        </div>
        {result.query_plan && (
          <div className="meta-item">
            <span className="meta-label">Type:</span>
            <span className="meta-value">{(result.query_plan as Record<string, string>).query_type}</span>
          </div>
        )}
      </div>

      {result.structured_data.length > 0 && (
        <div style={{ padding: '1.25rem', borderTop: '1px solid var(--border-color)' }}>
          <h4 className="card-title" style={{ marginBottom: '0.5rem' }}>Extracted Experimental Data</h4>
          <div style={{ overflowX: 'auto' }}>
            <table className="structured-data-table">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Catalyst</th>
                  <th>Solvent</th>
                  <th>Temperature</th>
                  <th>Yield</th>
                  <th>Reaction</th>
                </tr>
              </thead>
              <tbody>
                {result.structured_data.map((data, i) => (
                  <tr key={i}>
                    <td>{data.source_paper ? (data.source_paper.length > 30 ? data.source_paper.slice(0, 30) + '...' : data.source_paper) : '\u2014'}</td>
                    <td>{data.catalyst || '\u2014'}</td>
                    <td>{data.solvent || '\u2014'}</td>
                    <td>{data.temperature || '\u2014'}</td>
                    <td>{data.yield_value || '\u2014'}</td>
                    <td>{data.reaction || '\u2014'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
