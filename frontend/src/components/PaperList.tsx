import { useState, useEffect } from 'react';
import type { Paper } from '../types';
import { api } from '../api/client';

export default function PaperList() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      setLoading(true);
      const data = await api.listPapers();
      setPapers(data.papers);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this paper?')) return;
    try {
      await api.deletePaper(id);
      loadPapers();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  if (loading && papers.length === 0) return <div className="loading-spinner"><span className="spinner"></span> Loading papers...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-3">
        <h2 className="section-title">Document Library ({total})</h2>
        <button className="btn btn-secondary" onClick={loadPapers}>Refresh</button>
      </div>

      <div className="paper-grid">
        {papers.map(paper => (
          <div key={paper.id} className="paper-item slide-up">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="paper-title">{paper.title}</h3>
                <div className="paper-meta">
                  {paper.year && <span>{paper.year}</span>}
                  {paper.doi && <span>{paper.doi}</span>}
                  <span>{paper.chunk_count} chunks</span>
                </div>
              </div>
              <button className="btn btn-danger" onClick={() => handleDelete(paper.id)}>Delete</button>
            </div>

            <div className="paper-tags mt-1">
              {paper.chemical_entities?.slice(0, 5).map(entity => (
                <span key={entity} className="tag entity">{entity}</span>
              ))}
              {paper.reactions?.slice(0, 3).map(reaction => (
                <span key={reaction} className="tag reaction">{reaction}</span>
              ))}
            </div>
          </div>
        ))}

        {papers.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
            </div>
            <div className="empty-state-text">No papers found</div>
            <div className="empty-state-subtext">Upload papers to start searching</div>
          </div>
        )}
      </div>
    </div>
  );
}
