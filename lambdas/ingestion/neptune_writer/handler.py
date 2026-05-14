import json
import os
import urllib.request
from shared import handler_wrapper, get_logger

logger = get_logger(__name__)

NEPTUNE_ENDPOINT = os.environ["NEPTUNE_ENDPOINT"]
NEPTUNE_URL = f"https://{NEPTUNE_ENDPOINT}:8182/openCypher"

NODE_TYPE_MAP = {
    "spec": "Spec",
    "feature": "Feature",
    "whitepaper": "Whitepaper",
    "vendor": "Vendor",
    "release": "Release",
    "section": "Section",
    "procedure": "Procedure",
    "asn1type": "ASN1Type",
}


def execute_cypher(query: str, parameters: dict = None):
    body = {"query": query}
    if parameters:
        body["parameters"] = json.dumps(parameters)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(NEPTUNE_URL, data=data, method="POST",
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def write_nodes(metadata: dict):
    spec = metadata.get("spec", "unknown")
    release = metadata.get("release", "unknown")
    feature = metadata.get("feature")
    vendor = metadata.get("vendor")
    source_type = metadata.get("source_type", "3gpp")

    # Spec node
    execute_cypher(
        "MERGE (s:Spec {id: $id}) SET s.title = $title, s.release = $release",
        {"id": spec, "title": f"TS {spec}", "release": release},
    )

    # Release node
    execute_cypher("MERGE (r:Release {id: $id})", {"id": release})

    # Feature node
    if feature:
        execute_cypher(
            "MERGE (f:Feature {id: $id}) SET f.spec = $spec, f.release = $release",
            {"id": feature, "spec": spec, "release": release},
        )
        execute_cypher(
            "MATCH (f:Feature {id: $fid}), (s:Spec {id: $sid}) MERGE (f)-[:DEFINED_IN]->(s)",
            {"fid": feature, "sid": spec},
        )

    # Vendor/Whitepaper nodes
    if source_type == "whitepaper" and vendor:
        execute_cypher("MERGE (v:Vendor {id: $id})", {"id": vendor})
        wp_id = f"{vendor}-{spec}"
        execute_cypher(
            "MERGE (w:Whitepaper {id: $id}) SET w.vendor = $vendor, w.spec = $spec",
            {"id": wp_id, "vendor": vendor, "spec": spec},
        )
        execute_cypher(
            "MATCH (w:Whitepaper {id: $wid}), (v:Vendor {id: $vid}) MERGE (w)-[:PUBLISHED_BY]->(v)",
            {"wid": wp_id, "vid": vendor},
        )


def write_edges(edges: list[dict]):
    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        edge_type = edge["edge_type"]
        confidence = edge.get("confidence", 1.0)

        query = (
            f"MERGE (a {{id: $src}}) "
            f"MERGE (b {{id: $tgt}}) "
            f"MERGE (a)-[:{edge_type} {{confidence: $conf}}]->(b)"
        )
        execute_cypher(query, {"src": src, "tgt": tgt, "conf": confidence})


@handler_wrapper
def lambda_handler(event, context):
    metadata = event["metadata"]
    edges = event.get("edges", [])

    write_nodes(metadata)
    write_edges(edges)

    return {**event, "graph_status": "written", "nodes_written": 1, "edges_written": len(edges)}
