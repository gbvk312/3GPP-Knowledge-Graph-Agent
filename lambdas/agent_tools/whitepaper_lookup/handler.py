import json
import os
import boto3

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")

KB_ID = os.environ["KB_ID"]


def lambda_handler(event, context):
    params = extract_params(event)
    spec_or_feature = params.get("spec_or_feature", "")

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": spec_or_feature},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5,
                "filter": {"equals": {"key": "source_type", "value": "whitepaper"}},
            }
        },
    )

    results = []
    for r in response.get("retrievalResults", []):
        meta = r.get("metadata", {})
        results.append({
            "chunk_id": meta.get("chunk_id", ""),
            "text": r["content"]["text"],
            "vendor": meta.get("vendor", "unknown"),
            "title": meta.get("title", ""),
            "score": r.get("score", 0),
        })

    return build_response({"results": results})


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
            "actionGroup": "whitepaper_lookup",
            "apiPath": "/whitepaper_lookup",
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
    }
