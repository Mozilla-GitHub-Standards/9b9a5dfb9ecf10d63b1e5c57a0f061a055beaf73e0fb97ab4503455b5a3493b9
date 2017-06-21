import datetime
import time
from typing import List, Iterator

import datadog
from attr import attrs, attrib

from ddsink.types import JSONDict


@attrs
class MetricConfig:
    query: str = attrib()
    time_period: int = attrib()
    s3_bucket: str = attrib()
    s3_path: str = attrib()
    end_time: int = attrib()

    @end_time.default
    def end_time_default(self) -> int:
        dt = datetime.datetime.fromtimestamp(time.time())
        return int(round_time(dt, round_to=self.time_period*60).timestamp())


def initialize_datadog(api_key: str, app_key: str) -> None:
    datadog.initialize(api_key=api_key, app_key=app_key)


def load_config(config_data: JSONDict) -> MetricConfig:
    return MetricConfig(**config_data)


def query_datadog(config: MetricConfig) -> JSONDict:
    return datadog.api.Metric.query(
        start=config.end_time-(config.time_period*60),
        end=config.end_time,
        query=config.query
    )


def translate_points(pointlist: List[List[float]]) -> Iterator[JSONDict]:
    for epoch_time, val in pointlist:
        if not val:
            continue
        ts = datetime.datetime.fromtimestamp(epoch_time/1000.0).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        yield dict(timestamp=ts, value=val)


def extract_scope(scope: str) -> JSONDict:
    return dict(part.split(':', 1) for part in scope.split(',') if part)


def format_metric_results(metric_result: JSONDict) -> Iterator[JSONDict]:
    series = metric_result["series"]
    for raw in series:
        yield dict(
            name=raw["metric"],
            display_name=raw["display_name"],
            interval=raw["interval"],
            start=raw["start"]/1000.0,
            end=raw["end"]/1000.0,
            expression=raw["expression"],
            points=list(translate_points(raw["pointlist"])),
            scope=extract_scope(raw.get("scope", "")),
        )


def round_time(dt: datetime.datetime, round_to: int = 60) -> datetime.datetime:
    """Round a datetime object to any time laps in seconds
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.

    """
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + datetime.timedelta(0, rounding-seconds, -dt.microsecond)
