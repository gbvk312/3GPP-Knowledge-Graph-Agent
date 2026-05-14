import json
import os
import urllib.request

NEPTUNE_ENDPOINT = os.environ["NEPTUNE_ENDPOINT"]
NEPTUNE_URL = f"https://{NEPTUNE_ENDPOINT}:8182/openCypher"


def execute_cypher(query: str, parameters: dict = None):
    body = {"query": query}
    if parameters:
        body["parameters"] = json.dumps(parameters)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(NEPTUNE_URL, data=data, method="POST",
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def lambda_handler(event, context):
    params = extract_params(event)
    start_node = params.get("start_node", "")
    edge_types = params.get("edge_types", [])
    depth = int(params.get("depth", 1))

    # Build query based on edge type filter
    if edge_types:
        rel_filter = "|".join(edge_types)
        query = (
            f"MATCH path = (s {{id: $start}})-[:{rel_filter}*1..{depth}]-(t) "
            f"RETURN nodes(path) AS nodes, relationships(path) AS rels"
        )
    else:
        query = (
            f"MATCH path = (s {{id: $start}})-[*1..{depth}]-(t) "
            f"RETURN nodes(path) AS nodes, relationships(path) AS rels"
        )

    result = execute_cypher(query, {"start": start_node})

    # Convert to Cytoscape.js format
    nodes_map = {}
    edges_list = []

    for record in result.get("results", []):
        for node in record.get("nodes", []):
            nid = node.get("id", node.get("~id", ""))
            props = node.get("properties", node)
            node_id = props.get("id", nid)
            if node_id not in nodes_map:
                labels = node.get("labels", node.get("~labels", []))
                node_type = labels[0] if labels else "Unknown"
                nodes_map[node_id] = {
                    "data": {
                        "id": node_id,
                        "label": props.get("title", props.get("id", node_id)),
                        "type": node_type,
                    }
                }

        for rel in record.get("rels", []):
            edges_list.append({
                "data": {
                    "source": rel.get("startNode", rel.get("~start", "")),
                    "target": rel.get("endNode", rel.get("~end", "")),
                    "label": rel.get("type", rel.get("~type", "")),
                }
            })

    body = {"nodes": list(nodes_map.values()), "edges": edges_list}
    return build_response(body)


def extract_params(event):
    if "requestBody" in event.get("actionGroup", event):
        body = event["requestBody"]["content"]["application/json"]["properties"]
        return {p["name"]: p["value"] for p in body}
    body = event.get("body")
    if body:
        return json.loads(body) if isinstance(body, str) else body
    return event


def build_response(body):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": "graph_search",
            "apiPath": "/graph_search",
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
    }
