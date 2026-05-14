const LEGEND_ITEMS = [
  { type: 'Spec', color: '#3b82f6' },
  { type: 'Feature', color: '#10b981' },
  { type: 'Whitepaper', color: '#f97316' },
  { type: 'Vendor', color: '#a855f7' },
  { type: 'Release', color: '#6b7280' },
  { type: 'ASN1Type', color: '#ef4444' },
];

export default function GraphLegend() {
  return (
    <div className="graph-legend">
      {LEGEND_ITEMS.map(({ type, color }) => (
        <div key={type} className="legend-item">
          <span className="legend-dot" style={{ background: color, color }} />
          <span>{type}</span>
        </div>
      ))}
    </div>
  );
}
