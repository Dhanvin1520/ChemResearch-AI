import { useState } from 'react';

interface Element {
  symbol: string;
  name: string;
  number: number;
  category: string;
  mass: string;
  row: number;
  col: number;
}

const ELEMENTS: Element[] = [
  { symbol: 'H', name: 'Hydrogen', number: 1, category: 'nonmetal', mass: '1.008', row: 1, col: 1 },
  { symbol: 'He', name: 'Helium', number: 2, category: 'noble-gas', mass: '4.003', row: 1, col: 18 },
  { symbol: 'Li', name: 'Lithium', number: 3, category: 'alkali', mass: '6.941', row: 2, col: 1 },
  { symbol: 'Be', name: 'Beryllium', number: 4, category: 'alkaline', mass: '9.012', row: 2, col: 2 },
  { symbol: 'B', name: 'Boron', number: 5, category: 'metalloid', mass: '10.81', row: 2, col: 13 },
  { symbol: 'C', name: 'Carbon', number: 6, category: 'nonmetal', mass: '12.01', row: 2, col: 14 },
  { symbol: 'N', name: 'Nitrogen', number: 7, category: 'nonmetal', mass: '14.01', row: 2, col: 15 },
  { symbol: 'O', name: 'Oxygen', number: 8, category: 'nonmetal', mass: '16.00', row: 2, col: 16 },
  { symbol: 'F', name: 'Fluorine', number: 9, category: 'halogen', mass: '19.00', row: 2, col: 17 },
  { symbol: 'Ne', name: 'Neon', number: 10, category: 'noble-gas', mass: '20.18', row: 2, col: 18 },
  { symbol: 'Na', name: 'Sodium', number: 11, category: 'alkali', mass: '22.99', row: 3, col: 1 },
  { symbol: 'Mg', name: 'Magnesium', number: 12, category: 'alkaline', mass: '24.31', row: 3, col: 2 },
  { symbol: 'Al', name: 'Aluminium', number: 13, category: 'post-transition', mass: '26.98', row: 3, col: 13 },
  { symbol: 'Si', name: 'Silicon', number: 14, category: 'metalloid', mass: '28.09', row: 3, col: 14 },
  { symbol: 'P', name: 'Phosphorus', number: 15, category: 'nonmetal', mass: '30.97', row: 3, col: 15 },
  { symbol: 'S', name: 'Sulfur', number: 16, category: 'nonmetal', mass: '16.07', row: 3, col: 16 },
  { symbol: 'Cl', name: 'Chlorine', number: 17, category: 'halogen', mass: '35.45', row: 3, col: 17 },
  { symbol: 'Ar', name: 'Argon', number: 18, category: 'noble-gas', mass: '39.95', row: 3, col: 18 },
  { symbol: 'K', name: 'Potassium', number: 19, category: 'alkali', mass: '39.10', row: 4, col: 1 },
  { symbol: 'Ca', name: 'Calcium', number: 20, category: 'alkaline', mass: '40.08', row: 4, col: 2 },
  { symbol: 'Sc', name: 'Scandium', number: 21, category: 'transition', mass: '44.96', row: 4, col: 3 },
  { symbol: 'Ti', name: 'Titanium', number: 22, category: 'transition', mass: '47.87', row: 4, col: 4 },
  { symbol: 'V', name: 'Vanadium', number: 23, category: 'transition', mass: '50.94', row: 4, col: 5 },
  { symbol: 'Cr', name: 'Chromium', number: 24, category: 'transition', mass: '52.00', row: 4, col: 6 },
  { symbol: 'Mn', name: 'Manganese', number: 25, category: 'transition', mass: '54.94', row: 4, col: 7 },
  { symbol: 'Fe', name: 'Iron', number: 26, category: 'transition', mass: '55.85', row: 4, col: 8 },
  { symbol: 'Co', name: 'Cobalt', number: 27, category: 'transition', mass: '58.93', row: 4, col: 9 },
  { symbol: 'Ni', name: 'Nickel', number: 28, category: 'transition', mass: '58.69', row: 4, col: 10 },
  { symbol: 'Cu', name: 'Copper', number: 29, category: 'transition', mass: '63.55', row: 4, col: 11 },
  { symbol: 'Zn', name: 'Zinc', number: 30, category: 'transition', mass: '65.38', row: 4, col: 12 },
  { symbol: 'Ga', name: 'Gallium', number: 31, category: 'post-transition', mass: '69.72', row: 4, col: 13 },
  { symbol: 'Ge', name: 'Germanium', number: 32, category: 'metalloid', mass: '72.63', row: 4, col: 14 },
  { symbol: 'As', name: 'Arsenic', number: 33, category: 'metalloid', mass: '74.92', row: 4, col: 15 },
  { symbol: 'Se', name: 'Selenium', number: 34, category: 'nonmetal', mass: '78.97', row: 4, col: 16 },
  { symbol: 'Br', name: 'Bromine', number: 35, category: 'halogen', mass: '79.90', row: 4, col: 17 },
  { symbol: 'Kr', name: 'Krypton', number: 36, category: 'noble-gas', mass: '83.80', row: 4, col: 18 },
];

const CATEGORY_COLORS: Record<string, string> = {
  'nonmetal': '#18181b',
  'noble-gas': '#6d28d9',
  'alkali': '#dc2626',
  'alkaline': '#ea580c',
  'transition': '#2563eb',
  'post-transition': '#0891b2',
  'metalloid': '#059669',
  'halogen': '#ca8a04',
};

export default function PeriodicTable() {
  const [hovered, setHovered] = useState<Element | null>(null);

  return (
    <div className="card fade-in">
      <div className="card-header">
        <h3 className="card-title">Periodic Table</h3>
        {hovered && (
          <div className="flex items-center gap-1">
            <span className="tag" style={{ background: CATEGORY_COLORS[hovered.category] + '18', color: CATEGORY_COLORS[hovered.category], border: `1px solid ${CATEGORY_COLORS[hovered.category]}30` }}>
              {hovered.name} ({hovered.symbol}) — {hovered.mass} u
            </span>
          </div>
        )}
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(18, 1fr)',
        gridTemplateRows: 'repeat(4, 1fr)',
        gap: '3px',
        padding: '0.5rem 0',
      }}>
        {ELEMENTS.map((el) => {
          const color = CATEGORY_COLORS[el.category] || '#71717a';
          const isHovered = hovered?.number === el.number;
          return (
            <div
              key={el.number}
              onMouseEnter={() => setHovered(el)}
              onMouseLeave={() => setHovered(null)}
              style={{
                gridRow: el.row,
                gridColumn: el.col,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '0.2rem',
                borderRadius: '4px',
                border: `1px solid ${isHovered ? color : 'var(--border-color)'}`,
                background: isHovered ? color + '12' : 'var(--bg-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                transform: isHovered ? 'scale(1.15)' : 'scale(1)',
                zIndex: isHovered ? 10 : 1,
                position: 'relative',
                boxShadow: isHovered ? `0 4px 12px ${color}20` : 'none',
                minHeight: '38px',
              }}
            >
              <span style={{ fontSize: '0.5rem', color: 'var(--text-muted)', lineHeight: 1 }}>{el.number}</span>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: isHovered ? color : 'var(--text-primary)', lineHeight: 1.2 }}>{el.symbol}</span>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1" style={{ fontSize: '0.6rem', color: 'var(--text-tertiary)' }}>
            <div style={{ width: 8, height: 8, borderRadius: 2, background: color }} />
            {cat.replace('-', ' ')}
          </div>
        ))}
      </div>
    </div>
  );
}
