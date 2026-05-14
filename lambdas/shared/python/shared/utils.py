import json
import logging
import os
from functools import wraps

import boto3


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        json.dumps({"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"})
    ))
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


def emit_metric(namespace: str, metric_name: str, value: float = 1, unit: str = "Count"):
    cw = boto3.client("cloudwatch")
    cw.put_metric_data(
        Namespace=namespace,
        MetricData=[{"MetricName": metric_name, "Value": value, "Unit": unit}],
    )


def handler_wrapper(func):
    @wraps(func)
    def wrapper(event, context):
        logger = get_logger(func.__module__)
        logger.info(json.dumps({"event": event}))
        try:
            result = func(event, context)
            logger.info(json.dumps({"status": "success"}))
            return result
        except Exception as e:
            logger.error(json.dumps({"status": "error", "error": str(e)}))
            emit_metric("Team49/Pipeline", f"{func.__name__}-errors")
            raise
    return wrapper
