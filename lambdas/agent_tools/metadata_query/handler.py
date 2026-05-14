import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")

CHUNKS_TABLE = os.environ["CHUNKS_TABLE"]
FEATURES_TABLE = os.environ["FEATURES_TABLE"]


def lambda_handler(event, context):
    params = extract_params(event)
    spec = params.get("spec")
    release = params.get("release")
    section = params.get("section")
    feature = params.get("feature")
    vendor = params.get("vendor")

    features_table = dynamodb.Table(FEATURES_TABLE)

    # If feature_id can be constructed directly
    if spec and release and section and feature:
        feature_id = f"{spec}#{release}#{section}#{feature}"
        response = features_table.get_item(Key={"feature_id": feature_id})
        item = response.get("Item")
        results = [item] if item else []
    elif spec and release:
        # Query chunks table GSI
        chunks_table = dynamodb.Table(CHUNKS_TABLE)
        kwargs = {"IndexName": "spec-release-index", "KeyConditionExpression": Key("spec_release").eq(f"{spec}#{release}")}
        if section:
            kwargs["KeyConditionExpression"] &= Key("section").eq(section)
        response = chunks_table.query(**kwargs)
        results = response.get("Items", [])
    else:
        # Scan with filters
        filter_expr = None
        if spec:
            filter_expr = Attr("spec").eq(spec)
        if vendor:
            cond = Attr("vendor").eq(vendor)
            filter_expr = filter_expr & cond if filter_expr else cond
        if feature:
            cond = Attr("feature").eq(feature)
            filter_expr = filter_expr & cond if filter_expr else cond

        kwargs = {}
        if filter_expr:
            kwargs["FilterExpression"] = filter_expr
        response = features_table.scan(**kwargs)
        results = response.get("Items", [])

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
            "actionGroup": "metadata_query",
            "apiPath": "/metadata_query",
            "httpMethod": "POST",
            "httpStatusCode": 200,
            "responseBody": {"application/json": {"body": json.dumps(body, default=str)}},
        },
    }
