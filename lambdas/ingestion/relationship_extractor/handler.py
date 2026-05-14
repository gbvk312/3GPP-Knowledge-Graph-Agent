import json
import os
import re

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Regex patterns for relationship extraction
SPEC_REF_PATTERN = re.compile(r"TS\s+(\d{2}\.\d{3})")
CLAUSE_REF_PATTERN = re.compile(r"clause\s+([\d.]+)")
ASN1_IMPORT_PATTERN = re.compile(r"IMPORTS\s+([\w\s,\-]+?)\s+FROM\s+([\w-]+)", re.DOTALL)

CLAUDE_PROMPT = """Analyze this whitepaper chunk and extract relationships to 3GPP specifications.
Return ONLY a JSON array of edges. Each edge: {"source": "...", "target": "...", "edge_type": "EXPLAINS|RELATED_TO", "confidence": 0.0-1.0}

Source should be the whitepaper identifier. Target should be a spec number or feature name.
Only include edges with confidence >= 0.7.

Chunk:
"""


def extract_regex_edges(text: str, source_spec: str) -> list[dict]:
    edges = []
    # TS references
    for match in SPEC_REF_PATTERN.finditer(text):
        target = match.group(1)
        if target != source_spec:
            edges.append({"source": source_spec, "target": target, "edge_type": "REFERENCES", "confidence": 1.0})

    # ASN.1 IMPORTS
    for match in ASN1_IMPORT_PATTERN.finditer(text):
        types = [t.strip() for t in match.group(1).split(",")]
        module = match.group(2)
        for t in types:
            if t:
                edges.append({"source": t, "target": module, "edge_type": "IMPORTS", "confidence": 1.0})

    # Clause references → DEFINED_IN
    for match in CLAUSE_REF_PATTERN.finditer(text):
        clause = match.group(1)
        edges.append({"source": clause, "target": source_spec, "edge_type": "DEFINED_IN", "confidence": 1.0})

    return edges


def extract_claude_edges(text: str, source_id: str, bedrock_client=None) -> list[dict]:
    if bedrock_client is None:
        import boto3
        bedrock_client = boto3.client("bedrock-runtime")
    response = bedrock_client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": CLAUDE_PROMPT + text[:8000]}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0},
    )
    raw = response["output"]["message"]["content"][0]["text"]
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start == -1 or end == 0:
        return []
    edges = json.loads(raw[start:end])
    return [e for e in edges if e.get("confidence", 0) >= 0.7]


def lambda_handler(event, context):
    import boto3
    from shared import handler_wrapper, get_logger

    s3 = boto3.client("s3")
    bedrock = boto3.client("bedrock-runtime")
    logger = get_logger(__name__)
    CHUNKS_BUCKET = os.environ["CHUNKS_BUCKET"]
    metadata = event["metadata"]
    chunks = event["chunks"]
    source_type = metadata.get("source_type", "3gpp")
    source_spec = metadata.get("spec", "unknown")

    all_edges = []

    for chunk_id in chunks:
        chunk_key = f"{source_spec}/{metadata.get('release', 'unknown')}/{chunk_id}.md"
        try:
            content = s3.get_object(Bucket=CHUNKS_BUCKET, Key=chunk_key)["Body"].read().decode("utf-8")
        except s3.exceptions.NoSuchKey:
            continue

        # Regex pass for all chunks
        edges = extract_regex_edges(content, source_spec)
        all_edges.extend(edges)

        # Claude pass for whitepapers only
        if source_type == "whitepaper":
            source_id = f"{metadata.get('vendor', 'unknown')}-{source_spec}"
            claude_edges = extract_claude_edges(content, source_id)
            all_edges.extend(claude_edges)

    # Deduplicate
    seen = set()
    unique_edges = []
    for e in all_edges:
        key = (e["source"], e["target"], e["edge_type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    return {**event, "edges": unique_edges}
