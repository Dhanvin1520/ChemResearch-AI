import type { TabType } from '../types';

interface LayoutProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  children: React.ReactNode;
}

const tabs: { id: TabType; label: string }[] = [
  { id: 'search', label: 'Research' },
  { id: 'papers', label: 'Papers' },
  { id: 'chemistry', label: 'Chemistry' },
  { id: 'graph', label: 'Graph' },
  { id: 'evaluation', label: 'Evaluation' },
];

export default function Layout({ activeTab, onTabChange, children }: LayoutProps) {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo" style={{ cursor: 'pointer' }} onClick={() => onTabChange('search')}>
            <span className="logo-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              </svg>
            </span>
            <span className="logo-text">ChemResearch AI</span>
            <span className="logo-badge">v1.0</span>
          </div>
          <nav className="nav-tabs">
            {tabs.map(tab => (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => onTabChange(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>
      <main className="app-main">
        {children}
      </main>
    </div>
  );
}
