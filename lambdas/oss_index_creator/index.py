import json
import os
import time
import urllib.request
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def handler(event, context):
    request_type = event["RequestType"]
    props = event["ResourceProperties"]
    collection_endpoint = props["CollectionEndpoint"]
    index_name = props["IndexName"]

    try:
        if request_type in ("Create", "Update"):
            region = os.environ.get("AWS_REGION", "us-west-2")
            credentials = boto3.Session().get_credentials().get_frozen_credentials()

            host = collection_endpoint if collection_endpoint.startswith("https://") else f"https://{collection_endpoint}"
            url = f"{host}/{index_name}"

            body = json.dumps({
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 1024,
                            "method": {"engine": "faiss", "name": "hnsw", "space_type": "l2"},
                        },
                        "AMAZON_BEDROCK_TEXT_CHUNK": {"type": "text"},
                        "AMAZON_BEDROCK_METADATA": {"type": "text"},
                    }
                },
            })

            # Retry with backoff - AOSS access policies take time to propagate
            last_error = None
            for attempt in range(8):
                try:
                    req = AWSRequest(method="PUT", url=url, data=body, headers={"Content-Type": "application/json"})
                    SigV4Auth(credentials, "aoss", region).add_auth(req)

                    http_req = urllib.request.Request(url, data=body.encode(), method="PUT", headers=dict(req.headers))
                    resp = urllib.request.urlopen(http_req)
                    print(f"Index creation response: {resp.status} {resp.read().decode()}")
                    last_error = None
                    break
                except Exception as e:
                    last_error = e
                    wait = 15 * (attempt + 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)

            if last_error:
                raise last_error

        send_response(event, context, "SUCCESS", {"Message": f"{request_type} complete"})
    except Exception as e:
        print(f"Error: {e}")
        send_response(event, context, "FAILED", {"Message": str(e)})


def send_response(event, context, status, data):
    body = json.dumps({
        "Status": status,
        "Reason": data.get("Message", ""),
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
        "Data": data,
    }).encode()
    req = urllib.request.Request(event["ResponseURL"], data=body, method="PUT")
    req.add_header("Content-Type", "")
    req.add_header("Content-Length", str(len(body)))
    urllib.request.urlopen(req)
