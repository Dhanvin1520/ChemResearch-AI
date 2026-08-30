import { useState } from 'react';
import Layout from './components/Layout';
import SearchBar from './components/SearchBar';
import AnswerCard from './components/AnswerCard';
import EvidencePanel from './components/EvidencePanel';
import MoleculeViewer from './components/MoleculeViewer';
import PaperList from './components/PaperList';
import IngestForm from './components/IngestForm';
import EvalDashboard from './components/EvalDashboard';
import GraphDashboard from './components/GraphDashboard';
import MoleculeLookup from './components/MoleculeLookup';
import PeriodicTable from './components/PeriodicTable';
import { useSearch } from './hooks/useSearch';
import type { TabType } from './types';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const { search, loading, error, result, history } = useSearch();

  const renderSearchTab = () => (
    <>
      <SearchBar onSearch={search} loading={loading} history={history} onTabChange={setActiveTab} />

      {error && <div className="error-message fade-in" style={{ maxWidth: '680px', margin: '1rem auto 0' }}>{error}</div>}

      {result && (
        <div className="fade-in" style={{ marginTop: '2rem' }}>
          <AnswerCard result={result} />

          {result.molecule_info && Object.values(result.molecule_info).length > 0 && (
            <div className="mt-3">
              <h3 className="section-title mb-2">Identified Molecules</h3>
              {Object.values(result.molecule_info).map((mol, i) => (
                <MoleculeViewer key={i} info={mol} />
              ))}
            </div>
          )}

          <EvidencePanel evidence={result.evidence} citations={result.citations} />
        </div>
      )}
    </>
  );

  const renderPapersTab = () => (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <IngestForm />
      <PaperList />
    </div>
  );

  const renderChemistryTab = () => (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <MoleculeLookup />
      <PeriodicTable />
    </div>
  );

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === 'search' && renderSearchTab()}
      {activeTab === 'papers' && renderPapersTab()}
      {activeTab === 'chemistry' && renderChemistryTab()}
      {activeTab === 'graph' && <GraphDashboard />}
      {activeTab === 'evaluation' && <EvalDashboard />}
    </Layout>
  );
}

export default App;
