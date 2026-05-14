import { AgentResponse, CytoscapeNode, CytoscapeEdge } from '../api/agent';
import { SelectedNode } from '../App';

interface Props {
  response: AgentResponse | null;
  selectedNode: SelectedNode | null;
  allNodes: CytoscapeNode[];
  allEdges: CytoscapeEdge[];
}

export default function DetailPanel({ response, selectedNode, allNodes }: Props) {
  if (!response && !selectedNode) {
    return (
      <div className="empty-detail">
        <p className="empty-icon">🔬</p>
        <p>Search for a 3GPP spec, feature, or ask a question</p>
        <p className="empty-hint">Click a node to see details<br/>Double-click to expand</p>
      </div>
    );
  }

  const specLink = (spec: string) =>
    `https://www.3gpp.org/ftp/Specs/archive/${spec.replace('.', '')}/`;

  return (
    <div className="detail-content">
      {/* Selected Node Card */}
      {selectedNode && (
        <section className="detail-section node-card">
          <div className="node-card-header">
            <span className={`node-badge ${selectedNode.type.toLowerCase()}`}>{selectedNode.type}</span>
            <span className="node-card-title">{selectedNode.label}</span>
          </div>
          <div className="node-card-stats">
            <div className="stat-item">
              <span className="stat-value">{selectedNode.connections}</span>
              <span className="stat-label">connections</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{selectedNode.neighbors.length}</span>
              <span className="stat-label">neighbors</span>
            </div>
          </div>
          <div className="node-neighbors">
            <span className="neighbors-label">Connected to:</span>
            <div className="neighbor-chips">
              {selectedNode.neighbors.slice(0, 12).map(n => (
                <span key={n} className="neighbor-chip">{n}</span>
              ))}
              {selectedNode.neighbors.length > 12 && (
                <span className="neighbor-chip more">+{selectedNode.neighbors.length - 12} more</span>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Summary */}
      {response && (
        <section className="detail-section">
          <h3 className="section-title">Summary</h3>
          <div className="summary-text">{response.summary}</div>
        </section>
      )}

      {/* Citations */}
      {response && response.citations.length > 0 && (
        <section className="detail-section">
          <h3 className="section-title">Citations ({response.citations.length})</h3>
          <div className="citations-list">
            {response.citations.map((c, i) => (
              <div key={i} className="citation-card">
                <div className="citation-header">
                  <a href={specLink(c.spec)} target="_blank" rel="noopener noreferrer" className="citation-link">
                    📄 TS {c.spec} · {c.release} · §{c.section}
                  </a>
                  <button onClick={() => navigator.clipboard.writeText(c.text)} className="copy-btn" title="Copy text">
                    📋
                  </button>
                </div>
                <p className="citation-text">{c.text}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Graph Overview */}
      {allNodes.length > 0 && !selectedNode && (
        <section className="detail-section">
          <h3 className="section-title">Graph Overview</h3>
          <table className="overview-table">
            <tbody>
              {Object.entries(
                allNodes.reduce((acc, n) => { acc[n.data.type] = (acc[n.data.type] || 0) + 1; return acc; }, {} as Record<string, number>)
              ).sort((a, b) => b[1] - a[1]).map(([type, count]) => (
                <tr key={type}>
                  <td><span className={`node-badge ${type.toLowerCase()}`}>{type}</span></td>
                  <td className="count-cell">{count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}
