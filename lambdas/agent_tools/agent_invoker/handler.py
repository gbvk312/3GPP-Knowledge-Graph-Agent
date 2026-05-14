import json
import os
import uuid
import boto3

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")

AGENT_ID = os.environ["AGENT_ID"]
AGENT_ALIAS_ID = os.environ["AGENT_ALIAS_ID"]


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    query = body.get("query", "")

    if not query:
        return {"statusCode": 400, "body": json.dumps({"error": "query is required"})}

    session_id = body.get("session_id", str(uuid.uuid4()))

    response = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=query,
    )

    # Collect streaming response
    completion = ""
    for event_stream in response["completion"]:
        if "chunk" in event_stream:
            completion += event_stream["chunk"]["bytes"].decode("utf-8")

    # Parse agent response (expects JSON with summary, nodes, edges, citations)
    try:
        result = json.loads(completion)
    except json.JSONDecodeError:
        result = {"summary": completion, "nodes": [], "edges": [], "citations": []}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(result),
    }
