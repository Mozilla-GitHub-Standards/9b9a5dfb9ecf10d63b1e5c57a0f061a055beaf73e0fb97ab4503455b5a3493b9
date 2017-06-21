import datetime
import gzip
import json
import logging
import os
import uuid
from typing import Iterator

import boto3

from ddsink.metrics import (
    initialize_datadog,
    load_config,
    query_datadog,
    format_metric_results,
    MetricConfig,
)
from ddsink.types import JSONDict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def save_output_to_s3(config: MetricConfig, output: Iterator[JSONDict]) -> None:
    dt = datetime.datetime.fromtimestamp(config.end_time)
    file_name = config.s3_path.format(
        date=dt.strftime("%Y-%m-%d"),
        year=dt.strftime("%Y"),
        hour=dt.strftime("%H"),
        minute=dt.strftime("%M"),
        uuid=str(uuid.uuid4()),
    )
    logger.info("Saving metrics to Bucket: {bucket}, File: {filename}".format(
        bucket=config.s3_bucket,
        filename=file_name,
    ))
    data = gzip.compress(b"".join(json.dumps(entry).encode('utf-8') for entry
                                  in output))
    s3 = boto3.resource('s3')
    object = s3.Object(config.s3_bucket, file_name)
    object.put(Body=data, ContentEncoding="gzip")


def lambda_handler(event: JSONDict, context=None):
    logger.info("Running with event: %s", event)
    initialize_datadog(api_key=os.environ["API_KEY"],
                       app_key=os.environ["APP_KEY"])
    config = load_config(event)
    results = query_datadog(config)
    if results["status"] != "ok":
        logger.critical("Datadog error response: %s", results)
        raise Exception("Error querying datadog")

    if not results["series"]:
        logger.critical("No series in query results. %s", results)
        raise Exception("No series results from datadog")

    output = format_metric_results(results)
    save_output_to_s3(config, output)
    logger.info("Saved output to S3.")
