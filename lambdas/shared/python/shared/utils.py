import json
import logging
import os
import time
from functools import wraps

import boto3

_cw_client = None


def _get_cw():
    global _cw_client
    if _cw_client is None:
        _cw_client = boto3.client("cloudwatch")
    return _cw_client


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "function": record.funcName,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    return logger


def emit_metric(namespace: str, metric_name: str, value: float = 1, unit: str = "Count", dimensions: dict = None):
    metric_data = {"MetricName": metric_name, "Value": value, "Unit": unit}
    if dimensions:
        metric_data["Dimensions"] = [{"Name": k, "Value": v} for k, v in dimensions.items()]
    try:
        _get_cw().put_metric_data(Namespace=namespace, MetricData=[metric_data])
    except Exception:
        pass  # Don't fail the Lambda on metric emission errors


def handler_wrapper(func):
    @wraps(func)
    def wrapper(event, context):
        logger = get_logger(func.__module__ or func.__name__)
        start = time.time()
        logger.info("Lambda invoked", extra={})
        try:
            result = func(event, context)
            duration_ms = (time.time() - start) * 1000
            emit_metric("Team49/Pipeline", f"{func.__name__}-duration", duration_ms, "Milliseconds")
            emit_metric("Team49/Pipeline", f"{func.__name__}-success")
            return result
        except Exception as e:
            logger.error(f"Handler failed: {e}")
            emit_metric("Team49/Pipeline", f"{func.__name__}-errors")
            raise
    return wrapper
