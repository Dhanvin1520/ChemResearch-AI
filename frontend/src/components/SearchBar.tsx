import { useState, type FormEvent, useEffect, useRef } from 'react';
import type { TabType } from '../types';
import MoleculeScene from './MoleculeScene';
import gsap from 'gsap';

interface SearchBarProps {
  onSearch: (question: string) => void;
  loading: boolean;
  history: string[];
  onTabChange?: (tab: TabType) => void;
}

const SAMPLE_QUESTIONS = [
  'What catalysts are used for Suzuki coupling reactions?',
  'Compare molecular properties of aspirin and ibuprofen',
  'What conditions favor high yield in aldol condensation?',
  'Convert caffeine to SMILES and show its properties',
];

export default function SearchBar({ onSearch, loading, history, onTabChange }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const heroRef = useRef<HTMLDivElement>(null);
  const titleRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const statsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    tl.fromTo(titleRef.current, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8 });
    tl.fromTo(subtitleRef.current, { opacity: 0, y: 25 }, { opacity: 1, y: 0, duration: 0.6 }, '-=0.4');
    tl.fromTo(searchRef.current, { opacity: 0, y: 20, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 0.6 }, '-=0.3');

    if (featuresRef.current) {
      const cards = featuresRef.current.querySelectorAll('.feature-card');
      tl.fromTo(cards, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.08 }, '-=0.2');
    }

    if (statsRef.current) {
      const items = statsRef.current.querySelectorAll('.stat-item');
      tl.fromTo(items, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 }, '-=0.2');

      items.forEach(item => {
        const valueEl = item.querySelector('.stat-value');
        if (!valueEl) return;
        const target = valueEl.textContent || '';
        const numMatch = target.match(/^(\d+)/);
        if (numMatch) {
          const endVal = parseInt(numMatch[1]);
          const suffix = target.replace(numMatch[1], '');
          const counter = { val: 0 };
          gsap.to(counter, {
            val: endVal,
            duration: 1.5,
            delay: 0.8,
            ease: 'power2.out',
            onUpdate: () => {
              valueEl.textContent = Math.round(counter.val) + suffix;
            }
          });
        }
      });
    }
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim() && !loading) {
      onSearch(query.trim());
    }
  };

  return (
    <div>
      <div className="hero-section" ref={heroRef}>
        <div className="hero-molecule-bg">
          <MoleculeScene />
        </div>
        <div className="hero-content">
          <div className="hero-badge">AI-Powered Chemical Intelligence</div>
          <h1 ref={titleRef} style={{ opacity: 0 }}>
            Research Chemistry<br />
            <span className="hero-accent">With Precision</span>
          </h1>
          <p className="subtitle" ref={subtitleRef} style={{ opacity: 0 }}>
            Ask any chemistry question. Get citation-grounded answers backed by scientific literature, molecular analysis, and structured experimental data.
          </p>

          <div className="search-container" ref={searchRef} style={{ opacity: 0 }}>
            <form onSubmit={handleSubmit}>
              <div className="search-input-wrapper">
                <div className="search-input-inner">
                  <span className="search-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="11" cy="11" r="8"></circle>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                  </span>
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Ask a chemistry research question..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    disabled={loading}
                  />
                  <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
                    {loading ? (
                      <span className="loading-spinner">
                        <span className="spinner"></span>
                        Analyzing
                      </span>
                    ) : (
                      'Search'
                    )}
                  </button>
                </div>
              </div>
            </form>

            <div className="sample-questions">
              {SAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  className="sample-btn"
                  onClick={() => {
                    setQuery(q);
                    onSearch(q);
                  }}
                  disabled={loading}
                >
                  {q.length > 50 ? q.slice(0, 50) + '...' : q}
                </button>
              ))}
            </div>

            {history.length > 0 && (
              <div className="recent-section">
                <span className="recent-label">Recent</span>
                {history.slice(0, 3).map((q, i) => (
                  <button
                    key={i}
                    className="recent-btn"
                    onClick={() => { setQuery(q); onSearch(q); }}
                    disabled={loading}
                  >
                    {q.length > 40 ? q.slice(0, 40) + '...' : q}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="features-section" ref={featuresRef}>
        <div className="features-section-title">Platform Capabilities</div>
        <div className="features-grid">
          <div className="feature-card" onClick={() => onTabChange?.('search')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </div>
            <div className="feature-card-title">Literature Search</div>
            <div className="feature-card-desc">Hybrid semantic + keyword retrieval across indexed papers with reranking.</div>
          </div>
          <div className="feature-card" onClick={() => onTabChange?.('papers')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
            </div>
            <div className="feature-card-title">PDF Ingestion</div>
            <div className="feature-card-desc">Upload papers. Auto-extract entities, reactions, and experimental conditions.</div>
          </div>
          <div className="feature-card" onClick={() => onTabChange?.('chemistry')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 3h6v7.5l3.5 5.25A2 2 0 0 1 16.83 19H7.17a2 2 0 0 1-1.67-3.25L9 10.5V3z" />
              </svg>
            </div>
            <div className="feature-card-title">Molecular Analysis</div>
            <div className="feature-card-desc">RDKit-powered structure rendering, property computation, and Lipinski analysis.</div>
          </div>
          <div className="feature-card" onClick={() => onTabChange?.('graph')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="2"></circle>
                <circle cx="19" cy="5" r="2"></circle>
                <circle cx="5" cy="5" r="2"></circle>
                <line x1="12" y1="10" x2="5" y2="7"></line>
                <line x1="12" y1="10" x2="19" y2="7"></line>
              </svg>
            </div>
            <div className="feature-card-title">Knowledge Graph</div>
            <div className="feature-card-desc">Explore relationships between molecules, reactions, and catalysts.</div>
          </div>
          <div className="feature-card" onClick={() => onTabChange?.('evaluation')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </div>
            <div className="feature-card-title">Benchmarking</div>
            <div className="feature-card-desc">50-question evaluation suite for retrieval accuracy and citation quality.</div>
          </div>
          <div className="feature-card" onClick={() => onTabChange?.('search')}>
            <div className="feature-card-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <div className="feature-card-title">AI-Powered Answers</div>
            <div className="feature-card-desc">LLM-generated answers with inline citations and evidence scoring.</div>
          </div>
        </div>

        <div className="stats-bar" ref={statsRef}>
          <div className="stat-item">
            <div className="stat-value">5</div>
            <div className="stat-label">AI Agents</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">50+</div>
            <div className="stat-label">Benchmarks</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">RDKit</div>
            <div className="stat-label">Chemistry Engine</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">PDF</div>
            <div className="stat-label">Paper Ingestion</div>
          </div>
        </div>
      </div>
    </div>
  );
}
