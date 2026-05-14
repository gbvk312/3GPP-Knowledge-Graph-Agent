import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import { askAgent, AgentResponse, CytoscapeNode, CytoscapeEdge } from './api/agent';
import FeatureCloud, { FeatureCloudHandle } from './components/FeatureCloud';
import DetailPanel from './components/DetailPanel';
import GraphLegend from './components/GraphLegend';
import FilterBar from './components/FilterBar';
import ErrorBanner from './components/ErrorBanner';
import ChatHistory, { ChatMessage } from './components/ChatHistory';
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
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [visibleNodeTypes, setVisibleNodeTypes] = useState<Set<string>>(new Set(['Spec', 'Feature', 'Whitepaper', 'Vendor', 'Release', 'ASN1Type']));
  const [visibleEdgeTypes, setVisibleEdgeTypes] = useState<Set<string>>(new Set(['REFERENCES', 'DEFINED_IN', 'EXPLAINS', 'SUPERSEDES', 'DEPLOYED_BY', 'PUBLISHED_BY', 'IMPORTS']));
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const graphRef = useRef<FeatureCloudHandle>(null);

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

  // Load query from URL on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {
      setQuery(q);
      handleSearch(q);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Ctrl+K / Cmd+K to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      // Escape to deselect node
      if (e.key === 'Escape' && !error) {
        setSelectedNode(null);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [error]);

  const handleSearch = useCallback(async (q?: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    setQuery(searchQuery);
    setLoading(true);
    setSelectedNode(null);
    setError(null);

    // Update URL
    const url = new URL(window.location.href);
    url.searchParams.set('q', searchQuery);
    window.history.replaceState({}, '', url.toString());

    // Add user message to chat
    setChatMessages(prev => [...prev, { role: 'user', content: searchQuery, timestamp: Date.now() }]);

    try {
      const res = await askAgent(searchQuery, sessionId || undefined);
      setResponse(res);
      setNodes(res.nodes);
      setEdges(res.edges);
      if (res.session_id) setSessionId(res.session_id);
      // Add agent message to chat
      setChatMessages(prev => [...prev, { role: 'agent', content: res.summary, timestamp: Date.now() }]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to query agent';
      setError(msg);
      setChatMessages(prev => [...prev, { role: 'agent', content: `Error: ${msg}`, timestamp: Date.now() }]);
    } finally {
      setLoading(false);
    }
  }, [query, sessionId]);

  const handleNodeSelect = useCallback((nodeId: string) => {
    const node = nodes.find(n => n.data.id === nodeId);
    if (!node) return;
    const neighborEdges = edges.filter(e => e.data.source === nodeId || e.data.target === nodeId);
    const neighbors = neighborEdges.map(e => e.data.source === nodeId ? e.data.target : e.data.source);
    setSelectedNode({ id: nodeId, label: node.data.label, type: node.data.type, connections: neighborEdges.length, neighbors });
  }, [nodes, edges]);

  const handleNodeExpand = useCallback((newNodes: CytoscapeNode[], newEdges: CytoscapeEdge[]) => {
    setNodes(prev => {
      const ids = new Set(prev.map(n => n.data.id));
      return [...prev, ...newNodes.filter(n => !ids.has(n.data.id))];
    });
    setEdges(prev => {
      const keys = new Set(prev.map(e => `${e.data.source}-${e.data.target}-${e.data.label}`));
      return [...prev, ...newEdges.filter(e => !keys.has(`${e.data.source}-${e.data.target}-${e.data.label}`))];
    });
  }, []);

  const handleReset = useCallback(() => {
    setQuery('');
    setResponse(null);
    setNodes([]);
    setEdges([]);
    setSelectedNode(null);
    setError(null);
    setSessionId(null);
    const url = new URL(window.location.href);
    url.searchParams.delete('q');
    window.history.replaceState({}, '', url.toString());
  }, []);

  return (
    <>
      <header className="header" role="banner">
        <div className="header-brand">
          <span className="header-icon" aria-hidden="true">⚡</span>
          <span className="header-title">3GPP Knowledge Graph</span>
        </div>
        <div className="search-bar" role="search">
          <input
            ref={searchInputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Ask about 5G specs... (Ctrl+K)"
            className="search-input"
            aria-label="Search query (Ctrl+K to focus)"
          />
          <button onClick={() => handleSearch()} disabled={loading} className="search-btn" aria-label="Search">
            {loading ? <span className="spinner" /> : '→'}
          </button>
        </div>
        <div className="header-actions">
          {(nodes.length > 0 || response) && (
            <button onClick={handleReset} className="reset-btn" title="Clear graph and start over" aria-label="Reset">
              🗑️
            </button>
          )}
          <button onClick={() => setShowHistory(true)} className="history-btn" title="View conversation history" aria-label="Chat history">
            💬 <span className="history-count">{chatMessages.length > 0 ? chatMessages.filter(m => m.role === 'user').length : ''}</span>
          </button>
          <button onClick={toggleTheme} className="theme-toggle" aria-label="Toggle theme">
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <nav className="chips-bar" aria-label="Quick searches">
        {QUICK_QUERIES.map(q => (
          <button key={q} className="chip" onClick={() => handleSearch(q)} aria-pressed={query === q}>{q}</button>
        ))}
      </nav>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {response && response.summary && (
        <div className="chat-response">
          <div className="chat-response-header">
            <span className="chat-icon">🤖</span>
            <span className="chat-label">Agent Response</span>
          </div>
          <div className="chat-response-text">{response.summary}</div>
        </div>
      )}

      {stats && (
        <div className="stats-bar">
          <span>📊 {stats.totalNodes} nodes</span>
          <span>🔗 {stats.totalEdges} edges</span>
          {stats.topNode && <span>⭐ Hub: {stats.topNode[0]} ({stats.topNode[1]} connections)</span>}
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
              <div className="skeleton-graph">
                <div className="skeleton-node skeleton-node-1" />
                <div className="skeleton-node skeleton-node-2" />
                <div className="skeleton-node skeleton-node-3" />
                <div className="skeleton-edge skeleton-edge-1" />
                <div className="skeleton-edge skeleton-edge-2" />
              </div>
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
              ref={graphRef}
              nodes={filteredNodes}
              edges={filteredEdges}
              onNodeSelect={handleNodeSelect}
              onNodeExpand={handleNodeExpand}
              responseSummary={response?.summary}
            />
          )}
          <GraphLegend />
        </div>
        <div className="detail-panel">
          <DetailPanel response={response} selectedNode={selectedNode} allNodes={nodes} allEdges={edges} />
        </div>
      </main>

      <ChatHistory messages={chatMessages} visible={showHistory} onClose={() => setShowHistory(false)} />

      <div className="keyboard-hints" aria-hidden="true">
        <kbd>Ctrl+K</kbd> Search &nbsp; <kbd>Esc</kbd> Deselect
      </div>
    </>
  );
}
