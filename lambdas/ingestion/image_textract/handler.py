import json
import os
import boto3
from shared import handler_wrapper, get_logger

s3 = boto3.client("s3")
textract = boto3.client("textract")
logger = get_logger(__name__)

RAW_BUCKET = os.environ["RAW_BUCKET"]


@handler_wrapper
def lambda_handler(event, context):
    bucket = event["detail"]["bucket"]["name"] if "detail" in event else event["bucket"]
    key = event["detail"]["object"]["key"] if "detail" in event else event["key"]

    output_key = f"textract-output/{key}"

    if key.endswith(".md"):
        # Passthrough for markdown files
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
    else:
        # PDF - use Textract
        response = textract.analyze_document(
            Document={"S3Object": {"Bucket": bucket, "Name": key}},
            FeatureTypes=["TABLES", "FORMS"],
        )
        blocks = response["Blocks"]
        content = "\n".join(
            b["Text"] for b in blocks if b["BlockType"] == "LINE" and "Text" in b
        )

    s3.put_object(Bucket=RAW_BUCKET, Key=output_key, Body=content.encode("utf-8"))

    return {
        "bucket": RAW_BUCKET,
        "key": output_key,
        "source_key": key,
        "source_type": "3gpp" if key.startswith("3gpp/") else "whitepaper",
    }
