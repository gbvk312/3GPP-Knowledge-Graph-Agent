import json
import os
import boto3

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")

KB_ID = os.environ["KB_ID"]


def lambda_handler(event, context):
    params = extract_params(event)
    query = params.get("query", "")
    top_k = int(params.get("top_k", 5))
    filters = params.get("filters", {})

    retrieval_config = {"vectorSearchConfiguration": {"numberOfResults": top_k}}

    if filters:
        filter_conditions = []
        for key, value in filters.items():
            filter_conditions.append({"equals": {"key": key, "value": value}})
        if filter_conditions:
            retrieval_config["vectorSearchConfiguration"]["filter"] = (
                {"andAll": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
            )

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration=retrieval_config,
    )

    results = []
    for r in response.get("retrievalResults", []):
        results.append({
            "chunk_id": r.get("metadata", {}).get("chunk_id", ""),
            "text": r["content"]["text"],
            "score": r.get("score", 0),
            "metadata": r.get("metadata", {}),
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
            "actionGroup": "vector_search",
            "apiPath": "/vector_search",
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
    }
