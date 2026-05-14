import { CytoscapeNode, CytoscapeEdge } from '../api/agent';

interface Props {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  visible: boolean;
  onToggle: () => void;
}

export default function AccessibleGraphView({ nodes, edges, visible, onToggle }: Props) {
  return (
    <div className="a11y-view">
      <button onClick={onToggle} className="a11y-toggle" aria-expanded={visible} aria-label="Toggle accessible table view">
        {visible ? '🗺️ Graph' : '📋 Table'}
      </button>
      {visible && (
        <div className="a11y-tables" role="region" aria-label="Graph data in table format">
          <table className="a11y-table" aria-label="Graph nodes">
            <caption>Nodes ({nodes.length})</caption>
            <thead>
              <tr><th>Label</th><th>Type</th></tr>
            </thead>
            <tbody>
              {nodes.map(n => (
                <tr key={n.data.id}>
                  <td>{n.data.label}</td>
                  <td><span className={`node-badge ${n.data.type.toLowerCase()}`}>{n.data.type}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
          <table className="a11y-table" aria-label="Graph edges">
            <caption>Edges ({edges.length})</caption>
            <thead>
              <tr><th>Source</th><th>Relationship</th><th>Target</th></tr>
            </thead>
            <tbody>
              {edges.map((e, i) => (
                <tr key={i}>
                  <td>{e.data.source}</td>
                  <td>{e.data.label}</td>
                  <td>{e.data.target}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
