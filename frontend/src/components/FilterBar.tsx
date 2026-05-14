import { useState } from 'react';

const NODE_TYPES = ['Spec', 'Feature', 'Whitepaper', 'Vendor', 'Release', 'ASN1Type'];
const EDGE_TYPES = ['REFERENCES', 'DEFINED_IN', 'EXPLAINS', 'SUPERSEDES', 'DEPLOYED_BY', 'PUBLISHED_BY', 'IMPORTS'];

const NODE_COLORS: Record<string, string> = {
  Spec: '#3b82f6', Feature: '#10b981', Whitepaper: '#f97316',
  Vendor: '#a855f7', Release: '#6b7280', ASN1Type: '#ef4444',
};

// Node shapes for colorblind accessibility
const NODE_SHAPES: Record<string, string> = {
  Spec: '●', Feature: '◆', Whitepaper: '■',
  Vendor: '▲', Release: '○', ASN1Type: '★',
};

interface Props {
  visibleNodeTypes: Set<string>;
  visibleEdgeTypes: Set<string>;
  onToggleNodeType: (type: string) => void;
  onToggleEdgeType: (type: string) => void;
}

export default function FilterBar({ visibleNodeTypes, visibleEdgeTypes, onToggleNodeType, onToggleEdgeType }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`filter-bar ${collapsed ? 'filter-bar-collapsed' : ''}`}>
      <button className="filter-collapse-btn" onClick={() => setCollapsed(!collapsed)} aria-expanded={!collapsed} aria-label="Toggle filters">
        <span>⚙️ Filters</span>
        <span className="filter-chevron">{collapsed ? '▼' : '▲'}</span>
      </button>
      {!collapsed && (
        <>
          <div className="filter-group">
            <span className="filter-label">Nodes</span>
            {NODE_TYPES.map(t => (
              <button
                key={t}
                className={`filter-btn ${visibleNodeTypes.has(t) ? 'active' : ''}`}
                style={{ borderColor: visibleNodeTypes.has(t) ? NODE_COLORS[t] : undefined }}
                onClick={() => onToggleNodeType(t)}
                aria-pressed={visibleNodeTypes.has(t)}
                aria-label={`${t} nodes ${visibleNodeTypes.has(t) ? 'visible' : 'hidden'}`}
              >
                <span className="filter-dot" style={{ background: visibleNodeTypes.has(t) ? NODE_COLORS[t] : 'var(--text-hint)' }} />
                <span className="filter-shape">{NODE_SHAPES[t]}</span>
                {t}
              </button>
            ))}
          </div>
          <div className="filter-group">
            <span className="filter-label">Edges</span>
            {EDGE_TYPES.map(t => (
              <button
                key={t}
                className={`filter-btn ${visibleEdgeTypes.has(t) ? 'active' : ''}`}
                onClick={() => onToggleEdgeType(t)}
                aria-pressed={visibleEdgeTypes.has(t)}
                aria-label={`${t} edges ${visibleEdgeTypes.has(t) ? 'visible' : 'hidden'}`}
              >
                {t}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
