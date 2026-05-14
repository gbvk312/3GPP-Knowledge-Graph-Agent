import hashlib
import json
import os
import re

MAX_CHUNK_SIZE = 8192
OVERLAP_RATIO = 0.1


def compute_chunk_id(spec: str, release: str, section: str, offset: int) -> str:
    raw = f"{spec}|{release}|{section}|{offset}"
    return hashlib.sha1(raw.encode()).hexdigest()


def split_at_boundaries(content: str) -> list[dict]:
    """Split content at ## headings, Procedure blocks, ASN.1 fences, and feature tables."""
    chunks = []

    # Split by ## headings first
    sections = re.split(r"\n(?=## )", content)

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        # Check for ASN.1 blocks within section
        asn1_parts = re.split(r"(```asn1.*?```)", section, flags=re.DOTALL)
        for j, part in enumerate(asn1_parts):
            if not part.strip():
                continue
            chunks.append({"text": part.strip(), "offset": len(chunks)})

    return chunks


def sub_split(chunk_text: str, max_size: int = MAX_CHUNK_SIZE) -> list[str]:
    """Sub-split chunks exceeding max_size at paragraph boundaries with overlap."""
    if len(chunk_text.encode("utf-8")) <= max_size:
        return [chunk_text]

    paragraphs = chunk_text.split("\n\n")
    sub_chunks = []
    current = []
    current_size = 0

    for para in paragraphs:
        para_size = len(para.encode("utf-8"))
        if current_size + para_size > max_size and current:
            sub_chunks.append("\n\n".join(current))
            # Keep overlap
            overlap_count = max(1, int(len(current) * OVERLAP_RATIO))
            current = current[-overlap_count:]
            current_size = sum(len(p.encode("utf-8")) for p in current)
        current.append(para)
        current_size += para_size

    if current:
        sub_chunks.append("\n\n".join(current))

    return sub_chunks


def lambda_handler(event, context):
    import boto3
    from shared import handler_wrapper, get_logger

    s3 = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    logger = get_logger(__name__)

    CHUNKS_BUCKET = os.environ["CHUNKS_BUCKET"]
    CHUNKS_TABLE = os.environ["CHUNKS_TABLE"]

    bucket = event["bucket"]
    key = event["key"]
    metadata = event["metadata"]

    content = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")

    spec = metadata.get("spec", "unknown")
    release = metadata.get("release", "unknown")
    section = metadata.get("section", "unknown")

    raw_chunks = split_at_boundaries(content)
    table = dynamodb.Table(CHUNKS_TABLE)
    chunk_records = []

    for chunk in raw_chunks:
        sub_texts = sub_split(chunk["text"])
        for sub_idx, text in enumerate(sub_texts):
            offset = chunk["offset"] * 100 + sub_idx
            chunk_id = compute_chunk_id(spec, release, section, offset)

            # Write to S3
            chunk_key = f"{spec}/{release}/{chunk_id}.md"
            s3.put_object(
                Bucket=CHUNKS_BUCKET,
                Key=chunk_key,
                Body=text.encode("utf-8"),
                Metadata={"spec": spec, "release": release, "section": section},
            )

            # Write to DynamoDB
            record = {
                "chunk_id": chunk_id,
                "spec_release": f"{spec}#{release}",
                "section": section,
                "s3_key": chunk_key,
                "metadata": json.dumps(metadata),
            }
            table.put_item(Item=record)
            chunk_records.append(record)

    return {**event, "chunks": [r["chunk_id"] for r in chunk_records], "chunk_count": len(chunk_records)}
