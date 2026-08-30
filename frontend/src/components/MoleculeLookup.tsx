import { useState } from 'react';
import { api } from '../api/client';
import type { MoleculeConvertResponse } from '../types';

export default function MoleculeLookup() {
  const [input, setInput] = useState('');
  const [inputType, setInputType] = useState<'name' | 'smiles'>('name');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MoleculeConvertResponse | null>(null);

  const handleSearch = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.convertMolecule(input.trim(), inputType);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lookup failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const QUICK_MOLECULES = ['Aspirin', 'Caffeine', 'Ibuprofen', 'Glucose', 'Ethanol', 'Paracetamol'];

  return (
    <div className="fade-in">
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Molecule Lookup</h3>
          <div className="flex gap-1">
            <button
              className={`btn ${inputType === 'name' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setInputType('name')}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
            >
              By Name
            </button>
            <button
              className={`btn ${inputType === 'smiles' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setInputType('smiles')}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
            >
              By SMILES
            </button>
          </div>
        </div>

        <div className="flex gap-1" style={{ marginBottom: '1rem' }}>
          <input
            type="text"
            className="form-input"
            placeholder={inputType === 'name' ? 'Enter molecule name (e.g., Aspirin)' : 'Enter SMILES string (e.g., CC(=O)Oc1ccccc1C(=O)O)'}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={handleSearch} disabled={loading || !input.trim()}>
            {loading ? <><span className="spinner" style={{ width: 14, height: 14 }}></span> Analyzing</> : 'Analyze'}
          </button>
        </div>

        <div className="flex gap-1" style={{ flexWrap: 'wrap' }}>
          {QUICK_MOLECULES.map(mol => (
            <button
              key={mol}
              className="sample-btn"
              onClick={() => { setInput(mol); setInputType('name'); }}
              disabled={loading}
            >
              {mol}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-message mt-2">{error}</div>}

      {result && (
        <div className="card mt-2 slide-up">
          <div className="card-header">
            <h3 className="card-title">{result.properties.name || result.input_value}</h3>
            <span className="tag">{result.properties.molecular_formula}</span>
          </div>

          <div className="molecule-viewer">
            {result.svg ? (
              <div
                className="molecule-svg"
                dangerouslySetInnerHTML={{ __html: result.svg }}
              />
            ) : (
              <div className="molecule-svg flex items-center" style={{ justifyContent: 'center', height: '200px', width: '280px' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No structure available</span>
              </div>
            )}

            <div className="molecule-props">
              <div className="molecule-props-grid">
                <div className="prop-item">
                  <div className="prop-label">Molecular Weight</div>
                  <div className="prop-value">{result.properties.molecular_weight?.toFixed(2)}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">Exact Mass</div>
                  <div className="prop-value">{result.properties.exact_mass?.toFixed(4)}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">LogP</div>
                  <div className="prop-value">{result.properties.logp?.toFixed(2)}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">TPSA</div>
                  <div className="prop-value">{result.properties.tpsa?.toFixed(1)} &#8491;&sup2;</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">H-Bond Donors</div>
                  <div className="prop-value">{result.properties.hbd}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">H-Bond Acceptors</div>
                  <div className="prop-value">{result.properties.hba}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">Rotatable Bonds</div>
                  <div className="prop-value">{result.properties.rotatable_bonds}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">Ring Count</div>
                  <div className="prop-value">{result.properties.ring_count}</div>
                </div>
                <div className="prop-item">
                  <div className="prop-label">Aromatic Rings</div>
                  <div className="prop-value">{result.properties.aromatic_rings}</div>
                </div>
              </div>

              <div style={{ marginTop: '0.75rem' }}>
                <div className="prop-label">SMILES</div>
                <div className="font-mono text-sm" style={{ wordBreak: 'break-all', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  {result.properties.smiles}
                </div>
              </div>

              {result.properties.functional_groups && result.properties.functional_groups.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <div className="prop-label">Functional Groups</div>
                  <div className="functional-groups">
                    {result.properties.functional_groups.map((group, i) => (
                      <span key={i} className="fg-tag">{group}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.properties.logp !== undefined && (
                <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
                  <div className="prop-label" style={{ marginBottom: '0.35rem' }}>Lipinski's Rule of Five</div>
                  <div className="flex gap-1" style={{ flexWrap: 'wrap' }}>
                    <span className={`tag ${result.properties.molecular_weight <= 500 ? 'entity' : ''}`}>
                      MW {result.properties.molecular_weight <= 500 ? '\u2264' : '>'} 500: {result.properties.molecular_weight <= 500 ? 'Pass' : 'Fail'}
                    </span>
                    <span className={`tag ${result.properties.logp <= 5 ? 'entity' : ''}`}>
                      LogP {result.properties.logp <= 5 ? '\u2264' : '>'} 5: {result.properties.logp <= 5 ? 'Pass' : 'Fail'}
                    </span>
                    <span className={`tag ${result.properties.hbd <= 5 ? 'entity' : ''}`}>
                      HBD {result.properties.hbd <= 5 ? '\u2264' : '>'} 5: {result.properties.hbd <= 5 ? 'Pass' : 'Fail'}
                    </span>
                    <span className={`tag ${result.properties.hba <= 10 ? 'entity' : ''}`}>
                      HBA {result.properties.hba <= 10 ? '\u2264' : '>'} 10: {result.properties.hba <= 10 ? 'Pass' : 'Fail'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
