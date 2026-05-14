import json
import os
import boto3
from shared import handler_wrapper, get_logger

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
logger = get_logger(__name__)

FEATURES_TABLE = os.environ["FEATURES_TABLE"]
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

EXTRACTION_PROMPT = """Extract structured metadata from this 3GPP document chunk. Return ONLY valid JSON with these fields:
- spec: specification number (e.g. "38.331")
- release: release version (e.g. "Rel-18")
- section: section number (e.g. "5.5.4")
- feature: primary feature name in snake_case
- keywords: array of technical keywords
- technology: technology name (e.g. "5G NR")
- source_type: "3gpp" or "whitepaper"
- vendor: vendor name or null
- related_specs: array of referenced spec numbers

Document:
"""


@handler_wrapper
def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]
    source_type = event["source_type"]

    content = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")

    # Truncate for Claude context
    chunk = content[:12000]

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": EXTRACTION_PROMPT + chunk}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0},
    )

    raw_text = response["output"]["message"]["content"][0]["text"]
    # Extract JSON from response
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    metadata = json.loads(raw_text[start:end])
    metadata["source_type"] = source_type

    # Build feature_id and write to DynamoDB
    feature_id = f"{metadata.get('spec', 'unknown')}#{metadata.get('release', 'unknown')}#{metadata.get('section', 'unknown')}#{metadata.get('feature', 'unknown')}"
    metadata["feature_id"] = feature_id

    table = dynamodb.Table(FEATURES_TABLE)
    table.put_item(Item=metadata)

    return {**event, "metadata": metadata}
