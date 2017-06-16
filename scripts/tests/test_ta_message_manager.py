#!/usr/bin/env python3

import logging
import unittest

from ddt import ddt
from mock import patch
# from moto import mock_sqs

from scripts.ta_message_manager import ta_message_manager as mm

logging.getLogger('botocore').propagate = False # Disable boto logging for unit tests.

# TEST_QUEUE_URL = 'https://queue.amazonaws.com/127516845550/TreatmentArmQueue'

@ddt
class MyTestCase(unittest.TestCase):

    # @mock_sqs
    # @patch('scripts.ta_message_manager.ta_message_manager.logging')
    # def test_constructor(self, mock_logging):
    #     tamm = mm.TreatmentArmMessageManager()
    #     self.assertRegex(tamm.queue_url, "https:\/\/queue.amazonaws.com\/\d+\/"+mm.TA_QUEUE_NAME)

# @patch('scripts.ta_message_manager.ta_message_manager.boto3')
    # def test_constructor(self, mock_boto3):
    #     # def create_mock_client():
    #     #     mock_sqs_client = Mock()
    #     #     mock_sqs_instance = mock_sqs_client.return_value
    #     #     mock_sqs_instance.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
    #     #     return mock_sqs_instance
    #
    #     mock_queue = Mock(name="mock_queue")
    #     mock_queue.__getitem__ = lambda s, x: TEST_QUEUE_URL if x == 'QueueUrl' else None
    #
    #     mock_sqs_client = Mock(name="mock_sqs_client")
    #     mock_sqs_client.create_queue.return_value = mock_queue
    #     # mock_sqs_instance = mock_sqs_client.return_value
    #     # mock_sqs_instance.create_queue.return_value = mock_queue
    #     # mock_sqs_instance.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
    #
    #     # test_result = mock_sqs_instance.create_queue()
    #     import pprint
    #     # pprint.pprint(test_result)
    #
    #     instance = mock_boto3.return_value
    #     # instance.client = create_mock_client
    #     instance.client.return_value = mock_sqs_client
    #     # instance.client.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
    #     # instance.client = mock_sqs_instance
    #
    #     print("trying it out")
    #     client = instance.client()
    #     test_result = client.create_queue()
    #     pprint.pprint(test_result)
    #     print(test_result['QueueUrl'])
    #
    #     tamm = mm.TreatmentArmMessageManager()
    #     # mock_sqs_instance.create_queue.assert_called_once()
    #     self.assertEqual(tamm.queue_url, TEST_QUEUE_URL)

    # @data(
    #
    # )
    # @unpack
    # @patch('scripts.ta_message_manager.ta_message_manager.logging')
    # @patch('scripts.ta_message_manager.ta_message_manager.Refresher')
    # @patch('scripts.summary_report_refresher.refresher.PatientAccessor')
    # @patch('scripts.summary_report_refresher.refresher.TreatmentArmsAccessor')
    # def _refresh_summary_report(self, mock_ta_accessor, mock_patient_accessor, mock_refresher, mock_logging):
    #
    #     r = Refresher()
    #
    #     mock_logger = mock_logging.getLogger()
    #     mock_logger.info.assert_called()
    #

if __name__ == '__main__':
    unittest.main()
