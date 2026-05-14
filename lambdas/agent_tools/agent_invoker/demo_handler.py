import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
MODEL_ID = "meta.llama3-8b-instruct-v1:0"

GRAPH_DATA = {"nodes": [{"data": {"id": "23.287", "label": "TS 23.287", "type": "Spec"}}, {"data": {"id": "23.304", "label": "TS 23.304", "type": "Spec"}}, {"data": {"id": "23.501", "label": "TS 23.501", "type": "Spec"}}, {"data": {"id": "23.502", "label": "TS 23.502", "type": "Spec"}}, {"data": {"id": "29.281", "label": "TS 29.281", "type": "Spec"}}, {"data": {"id": "33.501", "label": "TS 33.501", "type": "Spec"}}, {"data": {"id": "36.133", "label": "TS 36.133", "type": "Spec"}}, {"data": {"id": "36.211", "label": "TS 36.211", "type": "Spec"}}, {"data": {"id": "36.300", "label": "TS 36.300", "type": "Spec"}}, {"data": {"id": "36.331", "label": "TS 36.331", "type": "Spec"}}, {"data": {"id": "37.213", "label": "TS 37.213", "type": "Spec"}}, {"data": {"id": "37.324", "label": "TS 37.324", "type": "Spec"}}, {"data": {"id": "37.340", "label": "TS 37.340", "type": "Spec"}}, {"data": {"id": "37.355", "label": "TS 37.355", "type": "Spec"}}, {"data": {"id": "38.101", "label": "TS 38.101", "type": "Spec"}}, {"data": {"id": "38.104", "label": "TS 38.104", "type": "Spec"}}, {"data": {"id": "38.133", "label": "TS 38.133", "type": "Spec"}}, {"data": {"id": "38.201", "label": "TS 38.201", "type": "Spec"}}, {"data": {"id": "38.202", "label": "TS 38.202", "type": "Spec"}}, {"data": {"id": "38.211", "label": "TS 38.211", "type": "Spec"}}, {"data": {"id": "38.212", "label": "TS 38.212", "type": "Spec"}}, {"data": {"id": "38.213", "label": "TS 38.213", "type": "Spec"}}, {"data": {"id": "38.214", "label": "TS 38.214", "type": "Spec"}}, {"data": {"id": "38.215", "label": "TS 38.215", "type": "Spec"}}, {"data": {"id": "38.300", "label": "TS 38.300", "type": "Spec"}}, {"data": {"id": "38.305", "label": "TS 38.305", "type": "Spec"}}, {"data": {"id": "38.306", "label": "TS 38.306", "type": "Spec"}}, {"data": {"id": "38.314", "label": "TS 38.314", "type": "Spec"}}, {"data": {"id": "38.321", "label": "TS 38.321", "type": "Spec"}}, {"data": {"id": "38.322", "label": "TS 38.322", "type": "Spec"}}, {"data": {"id": "38.323", "label": "TS 38.323", "type": "Spec"}}, {"data": {"id": "38.331", "label": "TS 38.331", "type": "Spec"}}, {"data": {"id": "38.340", "label": "TS 38.340", "type": "Spec"}}, {"data": {"id": "38.351", "label": "TS 38.351", "type": "Spec"}}, {"data": {"id": "38.401", "label": "TS 38.401", "type": "Spec"}}, {"data": {"id": "38.410", "label": "TS 38.410", "type": "Spec"}}, {"data": {"id": "38.412", "label": "TS 38.412", "type": "Spec"}}, {"data": {"id": "38.413", "label": "TS 38.413", "type": "Spec"}}, {"data": {"id": "38.414", "label": "TS 38.414", "type": "Spec"}}, {"data": {"id": "38.415", "label": "TS 38.415", "type": "Spec"}}, {"data": {"id": "38.420", "label": "TS 38.420", "type": "Spec"}}, {"data": {"id": "38.424", "label": "TS 38.424", "type": "Spec"}}, {"data": {"id": "38.455", "label": "TS 38.455", "type": "Spec"}}, {"data": {"id": "38.460", "label": "TS 38.460", "type": "Spec"}}, {"data": {"id": "38.470", "label": "TS 38.470", "type": "Spec"}}, {"data": {"id": "38.473", "label": "TS 38.473", "type": "Spec"}}, {"data": {"id": "measurement-reporting", "label": "Measurement Reporting", "type": "Feature"}}, {"data": {"id": "carrier-aggregation", "label": "Carrier Aggregation", "type": "Feature"}}, {"data": {"id": "beam-management", "label": "Beam Management", "type": "Feature"}}, {"data": {"id": "dual-connectivity", "label": "Dual Connectivity", "type": "Feature"}}, {"data": {"id": "network-slicing", "label": "Network Slicing", "type": "Feature"}}, {"data": {"id": "5g-advanced", "label": "5G-Advanced Overview", "type": "Whitepaper"}}, {"data": {"id": "ntn-advances", "label": "5G NTN Advances", "type": "Whitepaper"}}, {"data": {"id": "intent-networks", "label": "Intent-Based Networks", "type": "Whitepaper"}}, {"data": {"id": "Rel-18", "label": "Rel-18", "type": "Release"}}], "edges": [{"data": {"source": "38.201", "target": "38.202", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "38.211", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "38.212", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "38.213", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "38.214", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "38.215", "label": "REFERENCES"}}, {"data": {"source": "38.201", "target": "37.213", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.201", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.211", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.212", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.213", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.214", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.215", "label": "REFERENCES"}}, {"data": {"source": "38.202", "target": "38.306", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.211", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.213", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.214", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.473", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "23.287", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "38.101", "label": "REFERENCES"}}, {"data": {"source": "38.212", "target": "37.213", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.201", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.211", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.212", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.213", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.214", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.104", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "36.331", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.133", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "36.211", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.455", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "37.213", "label": "REFERENCES"}}, {"data": {"source": "38.215", "target": "38.305", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.101", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.133", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.211", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "37.340", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.212", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.213", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.214", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.215", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.323", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "36.331", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "37.355", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.340", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "37.324", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.314", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "36.133", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "37.213", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.401", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.104", "label": "REFERENCES"}}, {"data": {"source": "38.306", "target": "38.322", "label": "REFERENCES"}}, {"data": {"source": "38.314", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.314", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.323", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "23.287", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.340", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "23.304", "label": "REFERENCES"}}, {"data": {"source": "38.322", "target": "38.351", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "38.322", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "33.501", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "23.287", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "23.304", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "38.351", "label": "REFERENCES"}}, {"data": {"source": "38.323", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.340", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.340", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.340", "target": "38.322", "label": "REFERENCES"}}, {"data": {"source": "38.340", "target": "38.473", "label": "REFERENCES"}}, {"data": {"source": "38.340", "target": "38.401", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.473", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.414", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.424", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "37.340", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "33.501", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.410", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.420", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.470", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "38.460", "label": "REFERENCES"}}, {"data": {"source": "38.401", "target": "36.300", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.412", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.413", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.414", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.415", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "23.502", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "38.455", "label": "REFERENCES"}}, {"data": {"source": "38.410", "target": "36.300", "label": "REFERENCES"}}, {"data": {"source": "38.412", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.412", "target": "23.502", "label": "REFERENCES"}}, {"data": {"source": "38.414", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.414", "target": "29.281", "label": "REFERENCES"}}, {"data": {"source": "38.414", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "29.281", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "37.324", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "23.501", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "38.413", "label": "REFERENCES"}}, {"data": {"source": "38.415", "target": "38.470", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "38.424", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "38.415", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "38.401", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "37.340", "label": "REFERENCES"}}, {"data": {"source": "38.420", "target": "29.281", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.413", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.300", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "36.133", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "36.211", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.331", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "37.355", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.321", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.133", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.305", "label": "REFERENCES"}}, {"data": {"source": "38.455", "target": "38.215", "label": "REFERENCES"}}, {"data": {"source": "measurement-reporting", "target": "38.331", "label": "DEFINED_IN"}}, {"data": {"source": "carrier-aggregation", "target": "38.212", "label": "DEFINED_IN"}}, {"data": {"source": "beam-management", "target": "38.214", "label": "DEFINED_IN"}}, {"data": {"source": "dual-connectivity", "target": "38.300", "label": "DEFINED_IN"}}, {"data": {"source": "network-slicing", "target": "38.300", "label": "DEFINED_IN"}}, {"data": {"source": "5g-advanced", "target": "beam-management", "label": "EXPLAINS"}}, {"data": {"source": "5g-advanced", "target": "carrier-aggregation", "label": "EXPLAINS"}}, {"data": {"source": "ntn-advances", "target": "dual-connectivity", "label": "EXPLAINS"}}, {"data": {"source": "intent-networks", "target": "network-slicing", "label": "EXPLAINS"}}]}

SPEC_DETAILS = {
    "38.331": "RRC protocol specification - measurement reporting, handover, connection management",
    "38.300": "NR Overall Description - architecture, dual connectivity, network slicing",
    "38.306": "UE Radio Access Capabilities - band combinations, feature sets",
    "38.214": "Physical layer procedures for data - beam management, CSI reporting",
    "38.212": "Multiplexing and channel coding - carrier aggregation, DCI formats",
    "38.211": "Physical channels and modulation - reference signals, OFDM",
    "38.213": "Physical layer procedures for control - PDCCH, beam indication",
    "38.215": "Physical layer measurements - RSRP, RSRQ, positioning",
    "38.321": "MAC protocol - scheduling, HARQ, random access",
    "38.322": "RLC protocol - segmentation, ARQ, data transfer modes",
    "38.323": "PDCP protocol - ciphering, header compression, reordering",
    "38.401": "NG-RAN Architecture - CU-DU split, F1/E1 interfaces",
    "38.410": "NG-RAN NG interface - general aspects, functions",
    "38.201": "Physical layer general description - overview of NR physical layer",
    "38.202": "Services provided by physical layer - transport channels",
    "37.340": "Multi-connectivity - EN-DC, NR-DC procedures",
    "23.501": "System architecture for 5G - network functions, slicing",
}

SYSTEM_PROMPT = """You are a 3GPP standards expert. Answer the user's question using the knowledge graph context provided.

Rules:
- Be concise and technical (3-5 sentences max)
- Reference specific TS numbers when relevant
- Focus on the user's actual question
- Do NOT use markdown headers or bullet points - just plain text paragraphs
- Return ONLY a JSON object with keys: "summary" (your answer text), "relevant_specs" (array of spec IDs most relevant to the query), "citations" (array of objects with keys: spec, release, section, text)
"""


def find_relevant_subgraph(query, all_nodes, all_edges):
    """Return nodes/edges relevant to the query."""
    q = query.lower()
    relevant_ids = set()

    # Match features
    features = {"beam-management": ["beam", "beamforming", "beam management"],
                "carrier-aggregation": ["carrier aggregation", "ca ", "component carrier"],
                "measurement-reporting": ["measurement", "reporting", "rsrp", "rsrq"],
                "dual-connectivity": ["dual connectivity", "dc", "en-dc", "mr-dc"],
                "network-slicing": ["slicing", "network slice", "nssai"]}
    for fid, keywords in features.items():
        if any(k in q for k in keywords):
            relevant_ids.add(fid)

    # Match specs mentioned directly
    for node in all_nodes:
        nid = node["data"]["id"]
        label = node["data"]["label"].lower()
        if nid in q or label in q or nid.replace(".", "") in q.replace(".", ""):
            relevant_ids.add(nid)

    # Match by spec description
    for spec_id, desc in SPEC_DETAILS.items():
        if any(word in desc.lower() for word in q.split() if len(word) > 3):
            relevant_ids.add(spec_id)

    # If nothing matched, return top connected specs
    if not relevant_ids:
        relevant_ids = {"38.331", "38.300", "38.306", "38.401", "38.214"}

    # Expand one hop
    expanded = set(relevant_ids)
    for edge in all_edges:
        s, t = edge["data"]["source"], edge["data"]["target"]
        if s in relevant_ids or t in relevant_ids:
            expanded.add(s)
            expanded.add(t)

    # Cap at 20 nodes for readability
    expanded = set(list(expanded)[:20])

    nodes = [n for n in all_nodes if n["data"]["id"] in expanded]
    edges = [e for e in all_edges if e["data"]["source"] in expanded and e["data"]["target"] in expanded]
    return nodes, edges


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    query = body.get("query", "").strip()

    if not query:
        return {"statusCode": 400, "headers": cors_headers(), "body": json.dumps({"error": "query is required"})}

    nodes, edges = find_relevant_subgraph(query, GRAPH_DATA["nodes"], GRAPH_DATA["edges"])

    # Build context for Claude
    graph_context = f"Graph has {len(nodes)} relevant nodes and {len(edges)} edges.\n"
    graph_context += "Relevant specs:\n"
    for n in nodes:
        nid = n["data"]["id"]
        desc = SPEC_DETAILS.get(nid, n["data"]["label"])
        graph_context += f"- {n['data']['label']} ({n['data']['type']}): {desc}\n"

    user_msg = f"Graph context:\n{graph_context}\n\nUser question: {query}"

    try:
        resp = bedrock.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_msg}]}],
            inferenceConfig={"maxTokens": 1024},
        )
        text = resp["output"]["message"]["content"][0]["text"]

        # Parse JSON from Claude's response
        try:
            parsed = json.loads(text)
            summary = parsed.get("summary", text)
            citations = parsed.get("citations", [])
        except json.JSONDecodeError:
            summary = text
            citations = []
    except Exception as e:
        summary = f"Error calling model: {str(e)}"
        citations = []

    return {
        "statusCode": 200,
        "headers": cors_headers(),
        "body": json.dumps({
            "summary": summary,
            "nodes": nodes,
            "edges": edges,
            "citations": citations,
        }),
    }


def cors_headers():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
