import json
import os
import uuid
import boto3
from botocore.config import Config

bedrock_agent_runtime = boto3.client(
    "bedrock-agent-runtime",
    config=Config(read_timeout=55, connect_timeout=5, retries={"max_attempts": 2}),
)

AGENT_ID = os.environ["AGENT_ID"]
AGENT_ALIAS_ID = os.environ["AGENT_ALIAS_ID"]
MAX_QUERY_LENGTH = 1000

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}


def lambda_handler(event, context):
    if event.get("httpMethod") == "OPTIONS" or event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "Invalid JSON body"})}

    query = body.get("query", "").strip()
    if not query:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": "query is required"})}
    if len(query) > MAX_QUERY_LENGTH:
        return {"statusCode": 400, "headers": CORS_HEADERS, "body": json.dumps({"error": f"query exceeds {MAX_QUERY_LENGTH} characters"})}

    session_id = body.get("session_id", str(uuid.uuid4()))

    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=query,
        )

        completion = ""
        for event_stream in response["completion"]:
            if "chunk" in event_stream:
                completion += event_stream["chunk"]["bytes"].decode("utf-8")

        try:
            result = json.loads(completion)
        except json.JSONDecodeError:
            result = {"summary": completion, "nodes": [], "edges": [], "citations": []}

        result["session_id"] = session_id
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps(result)}

    except Exception as e:
        return {
            "statusCode": 502,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Agent invocation failed", "detail": str(e)}),
        }
