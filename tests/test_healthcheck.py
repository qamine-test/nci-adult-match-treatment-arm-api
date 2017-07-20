#!/usr/bin/env python3

import unittest

import flask
from ddt import ddt, data, unpack
from mock import patch

from resources import healthcheck


@ddt
class MyTestCase(unittest.TestCase):
    @data((82,38,7,29,2))
    @unpack
    @patch('resources.healthcheck.TreatmentArmsAccessor')
    def test_get(self, total_cnt, active_cnt, active_closed_cnt, active_open_cnt, active_suspended_cnt,
                 mock_ta_accessor):

        instance = mock_ta_accessor.return_value
        instance.count = lambda x: total_cnt if x == {} else active_cnt
        instance.aggregate.return_value = [
            {"_id": "CLOSED", "count": active_closed_cnt},
            {"_id": "OPEN", "count": active_open_cnt},
            {"_id": "SUSPENDED", "count": active_suspended_cnt}
        ]

        app = flask.Flask(__name__)
        with app.test_request_context(''):
            result = healthcheck.HealthCheck().get()
            self.assertEqual(len(result), 3)
            # self.assertEqual(len(result), 5)
            # self.assertEqual(result["Total Arm Count"], total_cnt)
            # self.assertEqual(result["Active Arm Count"], active_cnt)
            self.assertEqual(result["Active Arms in CLOSED Status"], active_closed_cnt)
            self.assertEqual(result["Active Arms in OPEN Status"], active_open_cnt)
            self.assertEqual(result["Active Arms in SUSPENDED Status"], active_suspended_cnt)

    @patch('resources.healthcheck.TreatmentArmsAccessor',side_effect=Exception('Oh no!'))
    @patch('resources.healthcheck.logging')
    def test_get_except(self, mock_logging, mock_ta_accessor):

        app = flask.Flask(__name__)
        with app.test_request_context(''):
            (result, status_code) = healthcheck.HealthCheck().get()
            self.assertEqual(result, 'Oh no!')
            self.assertEqual(status_code, 500)

            # Verify exception handling
            mock_logger = mock_logging.getLogger()
            mock_logger.exception.assert_called_once()


if __name__ == '__main__':
    unittest.main()
