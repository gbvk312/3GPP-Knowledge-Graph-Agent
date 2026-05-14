const LEGEND_ITEMS = [
  { type: 'Spec', color: '#1d9bf0', icon: '🔵' },
  { type: 'Feature', color: '#00ba7c', icon: '🟢' },
  { type: 'Whitepaper', color: '#f97316', icon: '🟠' },
  { type: 'Vendor', color: '#a855f7', icon: '🟣' },
  { type: 'Release', color: '#6b7280', icon: '⚪' },
  { type: 'ASN1Type', color: '#ef4444', icon: '🔴' },
];

export default function GraphLegend() {
  return (
    <div className="graph-legend">
      {LEGEND_ITEMS.map(({ type, color }) => (
        <div key={type} className="legend-item">
          <span className="legend-dot" style={{ background: color }} />
          <span>{type}</span>
        </div>
      ))}
    </div>
  );
}
