import type { MoleculeInfo } from '../types';

interface MoleculeViewerProps {
  info: MoleculeInfo;
}

export default function MoleculeViewer({ info }: MoleculeViewerProps) {
  return (
    <div className="card mt-2 fade-in">
      <div className="card-header">
        <h3 className="card-title">Chemical Analysis: {info.formula}</h3>
      </div>
      <div className="molecule-viewer">
        {info.svg ? (
          <div
            className="molecule-svg"
            dangerouslySetInnerHTML={{ __html: info.svg }}
          />
        ) : (
          <div className="molecule-svg flex items-center" style={{ justifyContent: 'center', height: '200px', width: '300px' }}>
            <span style={{ color: 'var(--text-muted)' }}>No structure available</span>
          </div>
        )}
        <div className="molecule-props">
          <div className="molecule-props-grid">
            <div className="prop-item">
              <div className="prop-label">Molecular Weight</div>
              <div className="prop-value">{info.molecular_weight?.toFixed(2) || '\u2014'}</div>
            </div>
            <div className="prop-item">
              <div className="prop-label">Formula</div>
              <div className="prop-value">{info.formula || '\u2014'}</div>
            </div>
            <div className="prop-item" style={{ gridColumn: '1 / -1' }}>
              <div className="prop-label">SMILES</div>
              <div className="prop-value" style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>{info.smiles || '\u2014'}</div>
            </div>
          </div>
          {info.functional_groups && info.functional_groups.length > 0 && (
            <div className="mt-2">
              <div className="prop-label">Detected Functional Groups</div>
              <div className="functional-groups">
                {info.functional_groups.map((group, i) => (
                  <span key={i} className="fg-tag">{group}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
