export interface CytoscapeNode {
  data: { id: string; label: string; type: string };
}

export interface CytoscapeEdge {
  data: { source: string; target: string; label: string };
}

export interface Citation {
  spec: string;
  release: string;
  section: string;
  text: string;
}

export interface AgentResponse {
  summary: string;
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  citations: Citation[];
}

export async function askAgent(query: string): Promise<AgentResponse> {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`Agent error: ${res.status}`);
  return res.json();
}

export async function expandNode(nodeId: string): Promise<{ nodes: CytoscapeNode[]; edges: CytoscapeEdge[] }> {
  const res = await fetch(`${import.meta.env.VITE_API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: `graph_search start_node=${nodeId} depth=1` }),
  });
  if (!res.ok) throw new Error(`Expand error: ${res.status}`);
  const data: AgentResponse = await res.json();
  return { nodes: data.nodes, edges: data.edges };
}
