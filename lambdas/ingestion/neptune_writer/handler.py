import json
import os
import urllib.request
from shared import handler_wrapper, get_logger

logger = get_logger(__name__)

NEPTUNE_ENDPOINT = os.environ["NEPTUNE_ENDPOINT"]
NEPTUNE_URL = f"https://{NEPTUNE_ENDPOINT}:8182/openCypher"

ALLOWED_EDGE_TYPES = {
    "REFERENCES", "IMPORTS", "DEFINED_IN", "EXPLAINS",
    "SUPERSEDES", "DEPLOYED_BY", "PUBLISHED_BY", "RELATED_TO",
}


def execute_cypher(query: str, parameters: dict = None):
    body = {"query": query}
    if parameters:
        body["parameters"] = json.dumps(parameters)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(NEPTUNE_URL, data=data, method="POST",
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def write_nodes(metadata: dict):
    """Batch all node MERGEs into a single multi-statement call."""
    spec = metadata.get("spec", "unknown")
    release = metadata.get("release", "unknown")
    feature = metadata.get("feature")
    vendor = metadata.get("vendor")
    source_type = metadata.get("source_type", "3gpp")

    # Build batch of node operations
    nodes = [
        {"label": "Spec", "id": spec, "props": {"title": f"TS {spec}", "release": release}},
        {"label": "Release", "id": release, "props": {}},
    ]
    if feature:
        nodes.append({"label": "Feature", "id": feature, "props": {"spec": spec, "release": release}})
    if source_type == "whitepaper" and vendor:
        wp_id = f"{vendor}-{spec}"
        nodes.append({"label": "Vendor", "id": vendor, "props": {}})
        nodes.append({"label": "Whitepaper", "id": wp_id, "props": {"vendor": vendor, "spec": spec}})

    # Batch MERGE nodes by label to minimize round-trips
    by_label = {}
    for n in nodes:
        by_label.setdefault(n["label"], []).append(n)

    for label, items in by_label.items():
        batch = [{"id": it["id"], **it["props"]} for it in items]
        # UNWIND to merge all nodes of same label in one query
        query = (
            f"UNWIND $batch AS item "
            f"MERGE (n:{label} {{id: item.id}}) "
            f"SET n += item"
        )
        execute_cypher(query, {"batch": batch})

    # Write structural edges in batch
    struct_edges = []
    if feature:
        struct_edges.append({"src": feature, "tgt": spec, "type": "DEFINED_IN"})
    if source_type == "whitepaper" and vendor:
        wp_id = f"{vendor}-{spec}"
        struct_edges.append({"src": wp_id, "tgt": vendor, "type": "PUBLISHED_BY"})

    if struct_edges:
        _write_edge_batch(struct_edges)

    return len(nodes)


def write_edges(edges: list[dict]):
    """Batch all edges into grouped UNWIND queries by edge type."""
    if not edges:
        return

    # Group by edge_type for batched MERGE
    by_type = {}
    for edge in edges:
        edge_type = edge["edge_type"]
        if edge_type not in ALLOWED_EDGE_TYPES:
            logger.warning(f"Skipping disallowed edge type: {edge_type}")
            continue
        by_type.setdefault(edge_type, []).append({
            "src": edge["source"],
            "tgt": edge["target"],
            "conf": edge.get("confidence", 1.0),
        })

    for edge_type, batch in by_type.items():
        _write_edge_batch_typed(edge_type, batch)


def _write_edge_batch(edges: list[dict]):
    """Write structural edges grouped by type."""
    by_type = {}
    for e in edges:
        by_type.setdefault(e["type"], []).append(e)
    for edge_type, batch in by_type.items():
        items = [{"src": e["src"], "tgt": e["tgt"], "conf": 1.0} for e in batch]
        _write_edge_batch_typed(edge_type, items)


def _write_edge_batch_typed(edge_type: str, batch: list[dict]):
    """Execute a single UNWIND query for all edges of one type."""
    query = (
        f"UNWIND $batch AS e "
        f"MERGE (a {{id: e.src}}) "
        f"MERGE (b {{id: e.tgt}}) "
        f"MERGE (a)-[r:{edge_type}]->(b) "
        f"SET r.confidence = e.conf"
    )
    execute_cypher(query, {"batch": batch})


@handler_wrapper
def lambda_handler(event, context):
    metadata = event["metadata"]
    edges = event.get("edges", [])

    nodes_written = write_nodes(metadata)
    write_edges(edges)

    return {**event, "graph_status": "written", "nodes_written": nodes_written, "edges_written": len(edges)}
