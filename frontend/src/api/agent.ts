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
  session_id?: string;
}

const API_URL = import.meta.env.VITE_API_URL;
const TIMEOUT_MS = 55000;

async function fetchWithTimeout(url: string, options: RequestInit, timeout = TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } finally {
    clearTimeout(timer);
  }
}

export async function askAgent(query: string, sessionId?: string): Promise<AgentResponse> {
  const body: Record<string, string> = { query };
  if (sessionId) body.session_id = sessionId;

  const res = await fetchWithTimeout(`${API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Agent error: ${res.status}`);
  }
  return res.json();
}

export async function expandNode(nodeId: string): Promise<{ nodes: CytoscapeNode[]; edges: CytoscapeEdge[] }> {
  const res = await fetchWithTimeout(`${API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: `graph_search start_node=${nodeId} depth=1` }),
  });

  if (!res.ok) throw new Error(`Expand error: ${res.status}`);
  const data: AgentResponse = await res.json();
  return { nodes: data.nodes, edges: data.edges };
}
