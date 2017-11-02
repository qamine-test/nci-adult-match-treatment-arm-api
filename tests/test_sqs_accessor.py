#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack
from mock import patch, Mock, MagicMock

from accessors.sqs_accessor import SqsAccessor

LOCAL_DIR = '/my_local_dir'
TA_QUEUE_URL = 'http://ta.queue.url'
TA_QUEUE_NAME = 'TA_QUEUE_NAME'


@ddt
class SqsAccessorTests(unittest.TestCase):

    def setUp(self):
        # self.app = app.APP.test_client()
        #
        env_patcher = patch('accessors.sqs_accessor.Environment')
        self.addCleanup(env_patcher.stop)
        self.mock_env = env_patcher.start().return_value
        self.mock_env.bucket = 'adultmatch-dev'
        self.mock_env.region = 'us-east-1'
        self.mock_env.polling_interval = 3
        self.mock_env.visibility_timeout = 3600
        self.mock_env.tmp_file_dir = LOCAL_DIR

        # self.sqs_client = MagicMock(name='client')
        # self.sqs_client.create_queue.return_value = {'QueueUrl': TA_QUEUE_URL}

        boto3_patcher = patch('accessors.sqs_accessor.boto3')
        self.addCleanup(boto3_patcher.stop)
        self.mock_boto3 = boto3_patcher.start().return_value
        self.mock_boto3.client.return_value = True
        # self.mock_boto3.client = self.sqs_client
        # self.mock_boto3.client.return_value = self.sqs_client

        # logging_patcher = patch('accessors.sqs_accessor.logging')
        # self.addCleanup(logging_patcher.stop)
        # self.mock_logger = logging_patcher.start().getLogger()

        # self.sqs_accessor = SqsAccessor(TA_QUEUE_NAME)

    def test_constuctor(self):
        pass
        # sqs_accessor = SqsAccessor(TA_QUEUE_NAME)
        # self.mock_boto3.client.assert_called_once_with('sqs', region_name='us-east-1')
        # self.sqs_client.create_queue.assert_called_once_with(QueueName=TA_QUEUE_NAME)
        # self.assertEqual(sqs_accessor.queue_name, TA_QUEUE_NAME)
        # self.assertEqual(sqs_accessor.queue_url, TA_QUEUE_URL)
        # self.assertEqual(sqs_accessor.sqs_client, self.sqs_client)


if __name__ == '__main__':
    unittest.main()
