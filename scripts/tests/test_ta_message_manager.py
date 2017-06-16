#!/usr/bin/env python3

import logging
import unittest

from ddt import ddt, data, unpack
from mock import patch, MagicMock

from scripts.ta_message_manager import ta_message_manager as mm

logging.getLogger('botocore').propagate = False # Disable boto logging for unit tests.

TEST_QUEUE_URL = 'https://queue.amazonaws.com/127516845550/TreatmentArmQueue'

@ddt
class MyTestCase(unittest.TestCase):

    def setUp(self):
        queue_patcher = patch('scripts.ta_message_manager.ta_message_manager.SqsAccessor')
        self.addCleanup(queue_patcher.stop)
        self.mock_queue = queue_patcher.start()
        logging_patcher = patch('scripts.ta_message_manager.ta_message_manager.logging')
        self.addCleanup(logging_patcher.stop)
        self.mock_logger = logging_patcher.start().getLogger()

    def test_constructor(self):
        queue_instance = self.mock_queue.return_value
        queue_instance.queue_name = mm.TA_QUEUE_NAME
        queue_instance.queue_url = TEST_QUEUE_URL

        tamm = mm.TreatmentArmMessageManager()
        self.assertEqual(tamm.queue.queue_url, TEST_QUEUE_URL)
        self.assertEqual(tamm.queue.queue_name, mm.TA_QUEUE_NAME)
        self.assertEqual(tamm.sleep_time, mm.DEFAULT_SLEEP_TIME)
        self.mock_logger.info.assert_called_once()

    def test_run(self):
        queue_instance = self.mock_queue.return_value
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
    def test_handle_message(self, msg, exp_ret_val, exp_error):
        queue_instance = self.mock_queue.return_value

        tamm = mm.TreatmentArmMessageManager()
        tamm._refresh_summary_report = MagicMock()
        ret_val = tamm._handle_message({'Body': msg})

        self.assertEqual(ret_val, exp_ret_val)
        self.assertEqual(queue_instance.delete_message.call_count, 1)

        if exp_error:
            self.mock_logger.error.assert_called_once()
        else:
            self.mock_logger.error.assert_not_called()

    @patch('scripts.ta_message_manager.ta_message_manager.Refresher')
    def test_refresh_summary_report(self, mock_refresher):
        tamm = mm.TreatmentArmMessageManager()

        ret_code = tamm._refresh_summary_report()
        self.assertEqual(ret_code, 0)

    @patch('scripts.ta_message_manager.ta_message_manager.Refresher')
    def test_refresh_summary_report_with_exc(self, mock_refresher):
        tamm = mm.TreatmentArmMessageManager()

        mock_refresher.return_value.run.side_effect = Exception()

        ret_code = tamm._refresh_summary_report()
        self.assertEqual(ret_code, 1)

    def test_send_message_ta_queue(self):
        mm.send_message_to_ta_queue(mm.STOP_MSG)
        self.mock_queue.return_value.send_message.assert_called_with(mm.STOP_MSG)


if __name__ == '__main__':
    unittest.main()
