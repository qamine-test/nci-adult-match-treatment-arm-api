#!/usr/bin/env python3

import logging
import time

from flask import Flask

from accessors.sqs_accessor import SqsAccessor
from config import log  # pylint: disable=unused-import
from config.flask_config import Configuration
from scripts.summary_report_refresher.refresher import Refresher

APP = Flask(__name__)
APP.config.from_object(Configuration)

TA_QUEUE_NAME = "TreatmentArmQueue"
DEFAULT_SLEEP_TIME = 10  # Time to sleep between checking for messages; in seconds.

# Recoginized messages:
REFRESH_MSG = "RefreshSummaryReport"
STOP_MSG = "STOP"


class TreatmentArmMessageManager(object):

    def __init__(self, sleep_time=DEFAULT_SLEEP_TIME):
        """
        Creates the Treatment Arms API message queue.
        :param sleep_time: interval, in seconds, for checking the queue for messages.
        """
        self.logger = logging.getLogger(__name__)
        self.sleep_time = sleep_time
        self.queue = SqsAccessor(TA_QUEUE_NAME)

        self.logger.info("SQS queue {qn} created at {url}".format(qn=TA_QUEUE_NAME, url=self.queue.queue_url))

    def run(self):
        """
        Runs continually, periodically checking the queue for messages, until a STOP message is received.
        """
        time_to_stop = False
        while not time_to_stop:
            response = self.queue.receive_message(['SentTimestamp'])

            # import pprint
            # pprint.pprint(response)

            if 'Messages' in response and len(response['Messages']):
                message = response['Messages'][0]
                time_to_stop = self._handle_message(message)

            time.sleep(self.sleep_time)

    def _handle_message(self, message):
        """
        Takes the proper actions based on the passed in message.
        :param message: the 'Body' should be one of the recognized messages
        :return: True if the STOP message was received; otherwise False
        """
        msg_body = message['Body']
        self.logger.info("Message received: {msg}".format(msg=msg_body))

        # Delete received message from queue
        self.queue.delete_message(message)

        # Now handle the message
        rcvd_stop_msg = False
        if msg_body == REFRESH_MSG:
            self._refresh_summary_report()
        elif msg_body == STOP_MSG:
            rcvd_stop_msg = True
            # self._delete_queue()
        else:
            self.logger.error("Unknown message received: {}".format(msg_body))

        return rcvd_stop_msg

    def _refresh_summary_report(self):
        """
        Runs the Summary Report Refresh.
        :return: 0 if successful; otherwise 1.
        """
        self.logger.info("Starting the Summary Report Refresher")

        return_code = 0
        try:
            with APP.app_context():
                Refresher().run()
        except Exception as e:
            self.logger.exception(str(e))
            return_code = 1

            self.logger.info("Summary Report Refresher completed with return code {}".format(return_code))
        return return_code


def send_message_to_ta_queue(msg):
    """
    Convenience function to make simple the send of a message.
    :param msg: the message body string
    :return: the response dict returned from SQS
    """
    response = SqsAccessor(TA_QUEUE_NAME).send_message(msg)
    # print(str(response))
    return response

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("Starting the Treatment Arm API Message Queue")
    TreatmentArmMessageManager().run()
    logger.info("Exiting the Treatment Arm API Message Queue")
