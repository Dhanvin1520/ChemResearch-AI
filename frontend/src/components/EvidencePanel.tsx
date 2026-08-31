import { useState } from 'react';
import type { Evidence, Citation } from '../types';

interface EvidencePanelProps {
  evidence: Evidence[];
  citations: Citation[];
}

export default function EvidencePanel({ evidence, citations }: EvidencePanelProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [activeView, setActiveView] = useState<'evidence' | 'citations'>('evidence');

  return (
    <div className="mt-3 fade-in">
      <div className="flex items-center justify-between mb-2">
        <h3 className="section-title">
          {activeView === 'evidence' ? 'Evidence Sources' : 'Citations'}
        </h3>
        <div className="flex gap-1">
          <button
            className={`btn ${activeView === 'evidence' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveView('evidence')}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.7rem' }}
          >
            Evidence ({evidence.length})
          </button>
          <button
            className={`btn ${activeView === 'citations' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveView('citations')}
            style={{ fontSize: '0.75rem', padding: '0.35rem 0.7rem' }}
          >
            Citations ({citations.length})
          </button>
        </div>
      </div>

      {activeView === 'evidence' ? (
        <div className="evidence-grid">
          {evidence.map((ev, i) => {
            const isExpanded = expandedId === ev.chunk_id;
            return (
              <div
                key={ev.chunk_id}
                className={`evidence-item ${isExpanded ? 'expanded' : ''}`}
                onClick={() => setExpandedId(isExpanded ? null : ev.chunk_id)}
              >
                <div className="evidence-header">
                  <div>
                    <div className="evidence-title">{ev.paper_title}</div>
                    <span className="evidence-section-tag">{ev.section}</span>
                  </div>
                  <div className="evidence-badge">[{i + 1}] {(100 / (1 + Math.exp(-ev.relevance_score))).toFixed(0)}%</div>
                </div>

                <div className="evidence-content">
                  {isExpanded ? ev.content : (ev.content.length > 200 ? ev.content.slice(0, 200) + '...' : ev.content)}
                </div>

                {(ev.catalyst || ev.solvent || ev.temperature || ev.yield_value) && (
                  <div className="evidence-conditions">
                    {ev.catalyst && (
                      <span className="condition-tag">
                        <span className="label">Cat:</span>
                        <span className="value">{ev.catalyst}</span>
                      </span>
                    )}
                    {ev.solvent && (
                      <span className="condition-tag">
                        <span className="label">Solv:</span>
                        <span className="value">{ev.solvent}</span>
                      </span>
                    )}
                    {ev.temperature && (
                      <span className="condition-tag">
                        <span className="label">Temp:</span>
                        <span className="value">{ev.temperature}</span>
                      </span>
                    )}
                    {ev.yield_value && (
                      <span className="condition-tag">
                        <span className="label">Yield:</span>
                        <span className="value">{ev.yield_value}</span>
                      </span>
                    )}
                  </div>
                )}

                {ev.chemical_entities.length > 0 && isExpanded && (
                  <div className="functional-groups" style={{ marginTop: '0.5rem' }}>
                    {ev.chemical_entities.slice(0, 8).map((entity, j) => (
                      <span key={j} className="fg-tag">{entity}</span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="evidence-grid">
          {citations.map(citation => (
            <div key={citation.citation_id} className="evidence-item">
              <div className="evidence-header">
                <div>
                  <div className="evidence-title">{citation.paper_title}</div>
                  <div className="flex gap-1 mt-1">
                    <span className="evidence-section-tag">{citation.section}</span>
                    {citation.year && <span className="evidence-section-tag">{citation.year}</span>}
                    {citation.doi && <span className="evidence-section-tag">{citation.doi}</span>}
                  </div>
                </div>
                <div className="evidence-badge">[{citation.citation_id}]</div>
              </div>
              <div className="evidence-content">{citation.evidence_text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
