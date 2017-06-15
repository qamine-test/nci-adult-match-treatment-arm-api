#!/usr/bin/env python3

import logging
import time

import boto3
from flask import Flask

from config.flask_config import Configuration
from config import log  # pylint: disable=unused-import
from scripts.summary_report_refresher.refresher import Refresher

APP = Flask(__name__)
APP.config.from_object(Configuration)

TA_QUEUE_NAME = "TreatmentArmQueue"
REGION = 'us-east-1'
REFRESH_MSG = "RefreshSummaryReport"
STOP_MSG = "STOP"


class TreatmentArmMessageManager(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sqs_client = boto3.client('sqs', region_name=REGION)
        # print("self.sqs_client Type = "+str(type(self.sqs_client)))
        self._create_queue()

    def _create_queue(self):
        response = self.sqs_client.create_queue(QueueName=TA_QUEUE_NAME)
        # print("response Type = "+str(type(self.sqs_client)))
        self.queue_url = response['QueueUrl']
        self.logger.info("SQS queue {qn} created at {url}".format(qn=TA_QUEUE_NAME, url=self.queue_url))

    def _delete_queue(self):
        self.sqs_client.delete_queue(QueueUrl=self.queue_url)

    def run(self):
        time_to_stop = False
        while not time_to_stop:
            response = self.sqs_client.receive_message(
                QueueUrl=self.queue_url,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,)

            import pprint
            pprint.pprint(response)

            if 'Messages' in response and len(response['Messages']):
                message = response['Messages'][0]
                time_to_stop = self._handle_message(message)

            time.sleep(10)

    def _handle_message(self, message):
        msg_body = message['Body']
        self.logger.info("Message received: {msg}".format(msg=msg_body))

        # Delete received message from queue
        self.sqs_client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )

        # Now handle the message
        rcvd_stop_msg = False
        if msg_body == REFRESH_MSG:
            self._refresh_summary_report()
        elif msg_body == STOP_MSG:
            rcvd_stop_msg = True
            self._delete_queue()
        else:
            self.logger.error("Unknown message received: {}".format(msg_body))

        return rcvd_stop_msg

    def _refresh_summary_report(self):
        self.logger.info("Starting the Summary Report Refresher")

        return_code = 0
        try:
            with APP.app_context():
                Refresher().run()
        except Exception as exc:
            self.logger.exception(str(exc))
            return_code = 1

            self.logger.info("Summary Report Refresher completed with exit code {}".format(return_code))
        return return_code


def send_message_to_ta_queue(msg):
    sqs = boto3.client('sqs', region_name=REGION)
    queue = sqs.get_queue_url(QueueName=TA_QUEUE_NAME)
    response = sqs.send_message(
        QueueUrl=queue['QueueUrl'],
        MessageBody=msg,)
    print(str(response))

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("Starting the Treatment Arm API Message Queue")
    TreatmentArmMessageManager().run()
    logger.info("Exiting the Treatment Arm API Message Queue")
