import os
import unittest

import mock


event = dict(
    query="avg:system.cpu.user{}by{host}",
    time_period=60*24,
    s3_bucket="test-bucket",
    s3_path="date={date}/hour={hour}/{uuid}.gz",
)

good_query_result = {'status': 'ok', 'res_type': 'time_series',
                     'from_date': 1498064248000, 'series': [
        {'metric': 'system.cpu.user', 'query_index': 0, 'attributes': {},
         'display_name': 'system.cpu.user', 'unit': [
            {'scale_factor': 1.0, 'family': 'percentage', 'short_name': '%',
             'plural': 'percent', 'id': 17, 'name': 'percent'}, None],
         'pointlist': [[1498064240000.0, 6.4357500076293945],
                       [1498064260000.0, 7.403600001335144],
                       [1498064290000.0, None],
                       [1498067840000.0, 7.03710000038147]],
         'end': 1498067859000, 'interval': 20, 'start': 1498064240000,
         'length': 181, 'aggr': 'avg',
         'scope': 'app:autopush,env:prod,stack:autopush,type:autopush',
         'expression': 'avg:system.cpu.user{app:autopush,env:prod,'
                       'stack:autopush,type:autopush}'}],
                     'to_date': 1498067848000, 'resp_version': 1,
                     'query': 'avg:system.cpu.user{}',
                     'message': '', 'group_by': []}

empty_query_result = {'status': 'ok', 'res_type': 'time_series',
                      'from_date': 1498064248000, 'series': [],
                      'to_date': 1498067848000, 'resp_version': 1,
                      'query': 'avg:system.cpu.user{}',
                      'message': '', 'group_by': []}

bad_query_result = {'status': 'error', 'res_type': 'time_series',
                    'from_date': 1498064248000, 'series': [],
                    'to_date': 1498067848000, 'resp_version': 1,
                    'query': 'avg:system.cpu.user{}',
                    'message': '', 'group_by': []}


class TestHandler(unittest.TestCase):
    def setUp(self):
        os.environ["API_KEY"] = "blah"
        os.environ["APP_KEY"] = "blah"

    @mock.patch("ddsink.handler.boto3")
    @mock.patch("ddsink.metrics.datadog")
    def test_basic_run(self, mock_datadog, mock_boto):
        mock_boto.resource.return_value = mock_s3 = mock.Mock()
        mock_s3.Object.return_value = mock_obj = mock.Mock()
        mock_datadog.api.Metric.query.return_value = good_query_result

        from ddsink.handler import lambda_handler
        lambda_handler(event)

        mock_datadog.api.Metric.query.assert_called()
        mock_s3.Object.assert_called()

    @mock.patch("ddsink.handler.boto3")
    @mock.patch("ddsink.metrics.datadog")
    def test_empty_series(self, mock_datadog, mock_boto):
        mock_boto.resource.return_value = mock_s3 = mock.Mock()
        mock_s3.Object.return_value = mock_obj = mock.Mock()
        mock_datadog.api.Metric.query.return_value = empty_query_result

        from ddsink.handler import lambda_handler

        with self.assertRaises(Exception):
            lambda_handler(event)

        mock_datadog.api.Metric.query.assert_called()


    @mock.patch("ddsink.handler.boto3")
    @mock.patch("ddsink.metrics.datadog")
    def test_bad_series(self, mock_datadog, mock_boto):
        mock_boto.resource.return_value = mock_s3 = mock.Mock()
        mock_s3.Object.return_value = mock_obj = mock.Mock()
        mock_datadog.api.Metric.query.return_value = bad_query_result

        from ddsink.handler import lambda_handler

        with self.assertRaises(Exception):
            lambda_handler(event)

        mock_datadog.api.Metric.query.assert_called()
