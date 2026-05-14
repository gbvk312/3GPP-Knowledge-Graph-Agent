import { useState } from 'react';
import { askAgent, AgentResponse, CytoscapeNode, CytoscapeEdge } from './api/agent';
import FeatureCloud from './components/FeatureCloud';
import DetailPanel from './components/DetailPanel';

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [nodes, setNodes] = useState<CytoscapeNode[]>([]);
  const [edges, setEdges] = useState<CytoscapeEdge[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await askAgent(query);
      setResponse(res);
      setNodes(res.nodes);
      setEdges(res.edges);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeExpand = (newNodes: CytoscapeNode[], newEdges: CytoscapeEdge[]) => {
    setNodes(prev => {
      const ids = new Set(prev.map(n => n.data.id));
      return [...prev, ...newNodes.filter(n => !ids.has(n.data.id))];
    });
    setEdges(prev => {
      const keys = new Set(prev.map(e => `${e.data.source}-${e.data.target}`));
      return [...prev, ...newEdges.filter(e => !keys.has(`${e.data.source}-${e.data.target}`))];
    });
  };

  return (
    <>
      <header style={{ padding: '12px 24px', borderBottom: '1px solid #2f3336', display: 'flex', gap: 12 }}>
        <span style={{ fontSize: 20 }}>🔍</span>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Search specs, features, or ask a question..."
          style={{
            flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid #2f3336',
            background: '#1a1f25', color: '#e7e9ea', fontSize: 14,
          }}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          style={{
            padding: '8px 20px', borderRadius: 8, border: 'none',
            background: '#1d9bf0', color: '#fff', cursor: 'pointer', fontWeight: 600,
          }}
        >
          {loading ? '...' : 'Search'}
        </button>
      </header>
      <main style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ flex: 1, borderRight: '1px solid #2f3336' }}>
          <FeatureCloud nodes={nodes} edges={edges} onNodeExpand={handleNodeExpand} />
        </div>
        <div style={{ width: 420, overflow: 'auto', padding: 16 }}>
          <DetailPanel response={response} />
        </div>
      </main>
    </>
  );
}
