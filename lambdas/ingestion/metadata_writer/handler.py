import json
import os
import boto3
from shared import handler_wrapper, get_logger

dynamodb = boto3.resource("dynamodb")
logger = get_logger(__name__)

CHUNKS_TABLE = os.environ["CHUNKS_TABLE"]


@handler_wrapper
def lambda_handler(event, context):
    metadata = event["metadata"]
    chunks = event.get("chunks", [])
    edges = event.get("edges", [])

    table = dynamodb.Table(CHUNKS_TABLE)

    for chunk_id in chunks:
        table.update_item(
            Key={"chunk_id": chunk_id},
            UpdateExpression="SET metadata_json = :m, edges = :e",
            ExpressionAttributeValues={
                ":m": json.dumps(metadata),
                ":e": json.dumps(edges),
            },
        )

    return {**event, "metadata_written": len(chunks)}
