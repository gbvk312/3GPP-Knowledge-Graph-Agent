import os
import time
import boto3
from shared import handler_wrapper, get_logger

bedrock_agent = boto3.client("bedrock-agent")
logger = get_logger(__name__)

KB_ID = os.environ["KB_ID"]
DATA_SOURCE_ID = os.environ["DATA_SOURCE_ID"]
MAX_POLL_ATTEMPTS = 60
POLL_INTERVAL_SECONDS = 5


@handler_wrapper
def lambda_handler(event, context):
    response = bedrock_agent.start_ingestion_job(
        knowledgeBaseId=KB_ID,
        dataSourceId=DATA_SOURCE_ID,
    )
    job_id = response["ingestionJob"]["ingestionJobId"]
    logger.info(f"Started ingestion job: {job_id}")

    for attempt in range(MAX_POLL_ATTEMPTS):
        status_response = bedrock_agent.get_ingestion_job(
            knowledgeBaseId=KB_ID,
            dataSourceId=DATA_SOURCE_ID,
            ingestionJobId=job_id,
        )
        status = status_response["ingestionJob"]["status"]

        if status == "COMPLETE":
            return {**event, "kb_sync_status": "complete", "job_id": job_id}
        elif status in ("FAILED", "STOPPED"):
            failure_reasons = status_response["ingestionJob"].get("failureReasons", [])
            raise RuntimeError(f"Ingestion job {job_id} {status}: {failure_reasons}")

        time.sleep(POLL_INTERVAL_SECONDS)

    raise TimeoutError(f"Ingestion job {job_id} did not complete within {MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s")
