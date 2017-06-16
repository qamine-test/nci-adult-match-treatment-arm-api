#!/usr/bin/env python3

import logging
import unittest

from ddt import ddt, data, unpack
from mock import patch, MagicMock
# from moto import mock_sqs

from scripts.ta_message_manager import ta_message_manager as mm

logging.getLogger('botocore').propagate = False # Disable boto logging for unit tests.

TEST_QUEUE_URL = 'https://queue.amazonaws.com/127516845550/TreatmentArmQueue'

@ddt
@patch('scripts.ta_message_manager.ta_message_manager.logging')
@patch('scripts.ta_message_manager.ta_message_manager.SqsAccessor')
class MyTestCase(unittest.TestCase):
    # @mock_sqs
    # @patch('scripts.ta_message_manager.ta_message_manager.logging')
    # def test_constructor(self, mock_logging):
    #     tamm = mm.TreatmentArmMessageManager()
    #     self.assertRegex(tamm.queue_url, "https:\/\/queue.amazonaws.com\/\d+\/"+mm.TA_QUEUE_NAME)


    def test_constructor(self, mock_queue, mock_logging):
        queue_instance = mock_queue.return_value
        queue_instance.queue_name = mm.TA_QUEUE_NAME
        queue_instance.queue_url = TEST_QUEUE_URL

        tamm = mm.TreatmentArmMessageManager()
        self.assertEqual(tamm.queue.queue_url, TEST_QUEUE_URL)
        self.assertEqual(tamm.queue.queue_name, mm.TA_QUEUE_NAME)
        self.assertEqual(tamm.sleep_time, mm.DEFAULT_SLEEP_TIME)

        mock_logger = mock_logging.getLogger()
        mock_logger.info.assert_called_once()

    def test_run(self, mock_queue, mock_logging):
        queue_instance = mock_queue.return_value
        queue_instance.receive_message.side_effect = [{}, {'Messages':['1']}, {'Messages':['1']}, {}, {'Messages':['1']}]

        mock_handle_message = MagicMock(side_effect=[False, False, True])

        tamm = mm.TreatmentArmMessageManager(1)
        tamm._handle_message = mock_handle_message
        tamm.run()

        self.assertEqual(mock_handle_message.call_count, 3)

    @data(
        (mm.REFRESH_MSG, False, False),
        (mm.STOP_MSG, True, False),
        ("UnknownMessage", False, True),
    )
    @unpack
    def test_handle_message(self, msg, exp_ret_val, exp_error, mock_queue, mock_logging):
        queue_instance = mock_queue.return_value

        tamm = mm.TreatmentArmMessageManager()
        tamm._refresh_summary_report = MagicMock()
        ret_val = tamm._handle_message({'Body': msg})

        self.assertEqual(ret_val, exp_ret_val)
        self.assertEqual(queue_instance.delete_message.call_count, 1)

        mock_logger = mock_logging.getLogger()
        if exp_error:
            mock_logger.error.assert_called_once()
        else:
            mock_logger.error.assert_not_called()

    @patch('scripts.ta_message_manager.ta_message_manager.Refresher')
    def test_refresh_summary_report(self, mock_refresher, mock_queue, mock_logging):
        tamm = mm.TreatmentArmMessageManager()

        ret_code = tamm._refresh_summary_report()
        self.assertEqual(ret_code, 0)

    @patch('scripts.ta_message_manager.ta_message_manager.Refresher')
    def test_refresh_summary_report_with_exc(self, mock_refresher, mock_queue, mock_logging):
        tamm = mm.TreatmentArmMessageManager()

        instance = mock_refresher
        mock_refresher.return_value.run.side_effect = Exception()

        ret_code = tamm._refresh_summary_report()
        self.assertEqual(ret_code, 1)

    def test_send_message_ta_queue(self, mock_queue, mock_logging):
        mm.send_message_to_ta_queue(mm.STOP_MSG)
        mock_queue.return_value.send_message.assert_called_with(mm.STOP_MSG)

            # @patch('scripts.ta_message_manager.ta_message_manager.boto3')
    # def test_constructor(self, mock_queue):
    #     # def create_mock_client():
        #     mock_sqs_client = Mock()
        #     mock_sqs_instance = mock_sqs_client.return_value
        #     mock_sqs_instance.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
        #     return mock_sqs_instance

        # mock_queue = Mock(name="mock_queue")
        # mock_queue.__getitem__ = lambda s, x: TEST_QUEUE_URL if x == 'QueueUrl' else None
        #
        # mock_sqs_client = Mock(name="mock_sqs_client")
        # mock_sqs_client.create_queue.return_value = mock_queue
        # # mock_sqs_instance = mock_sqs_client.return_value
        # # mock_sqs_instance.create_queue.return_value = mock_queue
        # # mock_sqs_instance.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
        #
        # # test_result = mock_sqs_instance.create_queue()
        # import pprint
        # # pprint.pprint(test_result)
        #
        # instance = mock_boto3.return_value
        # # instance.client = create_mock_client
        # instance.client.return_value = mock_sqs_client
        # # instance.client.create_queue.return_value = dict([('QueueUrl', TEST_QUEUE_URL)])
        # # instance.client = mock_sqs_instance
        #
        # print("trying it out")
        # client = instance.client()
        # test_result = client.create_queue()
        # pprint.pprint(test_result)
        # print(test_result['QueueUrl'])
        #
        # tamm = mm.TreatmentArmMessageManager()
        # # mock_sqs_instance.create_queue.assert_called_once()
        # self.assertEqual(tamm.queue_url, TEST_QUEUE_URL)

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
