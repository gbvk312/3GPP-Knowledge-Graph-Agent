const NODE_TYPES = ['Spec', 'Feature', 'Whitepaper', 'Vendor', 'Release', 'ASN1Type'];
const EDGE_TYPES = ['REFERENCES', 'DEFINED_IN', 'EXPLAINS', 'SUPERSEDES', 'DEPLOYED_BY', 'PUBLISHED_BY'];

const NODE_COLORS: Record<string, string> = {
  Spec: '#1d9bf0', Feature: '#00ba7c', Whitepaper: '#f97316',
  Vendor: '#a855f7', Release: '#6b7280', ASN1Type: '#ef4444',
};

interface Props {
  visibleNodeTypes: Set<string>;
  visibleEdgeTypes: Set<string>;
  onToggleNodeType: (type: string) => void;
  onToggleEdgeType: (type: string) => void;
}

export default function FilterBar({ visibleNodeTypes, visibleEdgeTypes, onToggleNodeType, onToggleEdgeType }: Props) {
  return (
    <div className="filter-bar">
      <div className="filter-group">
        <span className="filter-label">Nodes:</span>
        {NODE_TYPES.map(t => (
          <button
            key={t}
            className={`filter-btn ${visibleNodeTypes.has(t) ? 'active' : ''}`}
            style={{ borderColor: visibleNodeTypes.has(t) ? NODE_COLORS[t] : '#374151' }}
            onClick={() => onToggleNodeType(t)}
          >
            <span className="filter-dot" style={{ background: visibleNodeTypes.has(t) ? NODE_COLORS[t] : '#374151' }} />
            {t}
          </button>
        ))}
      </div>
      <div className="filter-group">
        <span className="filter-label">Edges:</span>
        {EDGE_TYPES.map(t => (
          <button
            key={t}
            className={`filter-btn edge-filter ${visibleEdgeTypes.has(t) ? 'active' : ''}`}
            onClick={() => onToggleEdgeType(t)}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
