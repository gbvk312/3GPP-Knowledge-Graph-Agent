import { useState, useMemo } from 'react';
import { askAgent, AgentResponse, CytoscapeNode, CytoscapeEdge } from './api/agent';
import FeatureCloud from './components/FeatureCloud';
import DetailPanel from './components/DetailPanel';
import GraphLegend from './components/GraphLegend';
import FilterBar from './components/FilterBar';
import ErrorBanner from './components/ErrorBanner';
import { useTheme } from './hooks/useTheme';

const QUICK_QUERIES = [
  '5G NR architecture',
  'measurement reporting',
  'carrier aggregation',
  'beam management',
  'network slicing',
  'dual connectivity',
];

export interface SelectedNode {
  id: string;
  label: string;
  type: string;
  connections: number;
  neighbors: string[];
}

export default function App() {
  const { theme, toggle: toggleTheme } = useTheme();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AgentResponse | null>(null);
  const [nodes, setNodes] = useState<CytoscapeNode[]>([]);
  const [edges, setEdges] = useState<CytoscapeEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [visibleNodeTypes, setVisibleNodeTypes] = useState<Set<string>>(new Set(['Spec', 'Feature', 'Whitepaper', 'Vendor', 'Release', 'ASN1Type']));
  const [visibleEdgeTypes, setVisibleEdgeTypes] = useState<Set<string>>(new Set(['REFERENCES', 'DEFINED_IN', 'EXPLAINS', 'SUPERSEDES', 'DEPLOYED_BY', 'PUBLISHED_BY', 'IMPORTS']));

  const filteredNodes = useMemo(() => nodes.filter(n => visibleNodeTypes.has(n.data.type)), [nodes, visibleNodeTypes]);
  const filteredEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map(n => n.data.id));
    return edges.filter(e => visibleEdgeTypes.has(e.data.label) && nodeIds.has(e.data.source) && nodeIds.has(e.data.target));
  }, [edges, filteredNodes, visibleEdgeTypes]);

  const stats = useMemo(() => {
    if (nodes.length === 0) return null;
    const typeCounts: Record<string, number> = {};
    nodes.forEach(n => { typeCounts[n.data.type] = (typeCounts[n.data.type] || 0) + 1; });
    const degreeCounts: Record<string, number> = {};
    edges.forEach(e => {
      degreeCounts[e.data.source] = (degreeCounts[e.data.source] || 0) + 1;
      degreeCounts[e.data.target] = (degreeCounts[e.data.target] || 0) + 1;
    });
    const topNode = Object.entries(degreeCounts).sort((a, b) => b[1] - a[1])[0];
    return { typeCounts, totalNodes: nodes.length, totalEdges: edges.length, topNode };
  }, [nodes, edges]);

  const handleSearch = async (q?: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    setQuery(searchQuery);
    setLoading(true);
    setSelectedNode(null);
    setError(null);
    try {
      const res = await askAgent(searchQuery);
      setResponse(res);
      setNodes(res.nodes);
      setEdges(res.edges);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to query agent');
    } finally {
      setLoading(false);
    }
  };

  const handleNodeSelect = (nodeId: string) => {
    const node = nodes.find(n => n.data.id === nodeId);
    if (!node) return;
    const neighborEdges = edges.filter(e => e.data.source === nodeId || e.data.target === nodeId);
    const neighbors = neighborEdges.map(e => e.data.source === nodeId ? e.data.target : e.data.source);
    setSelectedNode({ id: nodeId, label: node.data.label, type: node.data.type, connections: neighborEdges.length, neighbors });
  };

  const handleNodeExpand = (newNodes: CytoscapeNode[], newEdges: CytoscapeEdge[]) => {
    setNodes(prev => {
      const ids = new Set(prev.map(n => n.data.id));
      return [...prev, ...newNodes.filter(n => !ids.has(n.data.id))];
    });
    setEdges(prev => {
      const keys = new Set(prev.map(e => `${e.data.source}-${e.data.target}-${e.data.label}`));
      return [...prev, ...newEdges.filter(e => !keys.has(`${e.data.source}-${e.data.target}-${e.data.label}`))];
    });
  };

  return (
    <>
      <header className="header" role="banner">
        <div className="header-brand">
          <span className="header-icon" aria-hidden="true">⚡</span>
          <span className="header-title">3GPP Knowledge Graph</span>
        </div>
        <div className="search-bar" role="search">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search specs, features, or ask a question..."
            className="search-input"
            aria-label="Search query"
          />
          <button onClick={() => handleSearch()} disabled={loading} className="search-btn" aria-label="Search">
            {loading ? <span className="spinner" /> : '→'}
          </button>
        </div>
        <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle theme">
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </header>

      {/* Quick search chips */}
      <nav className="chips-bar" aria-label="Quick searches">
        {QUICK_QUERIES.map(q => (
          <button key={q} className="chip" onClick={() => handleSearch(q)}>{q}</button>
        ))}
      </nav>

      {/* Error banner */}
      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {/* Chat response */}
      {response && response.summary && (
        <div className="chat-response">
          <div className="chat-response-header">
            <span className="chat-icon">🤖</span>
            <span className="chat-label">Agent Response</span>
          </div>
          <div className="chat-response-text">{response.summary}</div>
        </div>
      )}

      {/* Stats bar */}
      {stats && (
        <div className="stats-bar">
          <span>📊 {stats.totalNodes} nodes</span>
          <span>🔗 {stats.totalEdges} edges</span>
          {stats.topNode && <span>⭐ Most connected: TS {stats.topNode[0]} ({stats.topNode[1]})</span>}
        </div>
      )}

      <main className="main-layout" role="main">
        <div className="graph-panel">
          <FilterBar
            visibleNodeTypes={visibleNodeTypes}
            visibleEdgeTypes={visibleEdgeTypes}
            onToggleNodeType={(t) => setVisibleNodeTypes(prev => { const s = new Set(prev); s.has(t) ? s.delete(t) : s.add(t); return s; })}
            onToggleEdgeType={(t) => setVisibleEdgeTypes(prev => { const s = new Set(prev); s.has(t) ? s.delete(t) : s.add(t); return s; })}
          />
          {loading ? (
            <div className="loading-state">
              <div className="pulse-ring" />
              <p>Querying knowledge graph...</p>
            </div>
          ) : nodes.length === 0 ? (
            <div className="empty-state">
              <p className="empty-icon">🌐</p>
              <p>Search to visualize the 3GPP specification graph</p>
              <p className="empty-hint">Try "5G NR architecture" or click a chip above</p>
            </div>
          ) : (
            <FeatureCloud
              nodes={filteredNodes}
              edges={filteredEdges}
              onNodeSelect={handleNodeSelect}
              onNodeExpand={handleNodeExpand}
            />
          )}
          <GraphLegend />
        </div>
        <div className="detail-panel">
          <DetailPanel response={response} selectedNode={selectedNode} allNodes={nodes} allEdges={edges} />
        </div>
      </main>
    </>
  );
}
