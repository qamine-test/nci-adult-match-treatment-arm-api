"""
Implements the SqsAccessor class, a wrapper around the Amazon Simple Queue Service (SQS):
https://boto3.readthedocs.io/en/latest/reference/services/sqs.html
"""
import boto3

REGION = 'us-east-1'

class SqsAccessor(object):
    def __init__(self, queue_name):
        self.sqs_client = boto3.client('sqs', region_name=REGION)
        self.queue_name = queue_name
        response = self.sqs_client.create_queue(QueueName=queue_name)
        self.queue_url = response['QueueUrl']

    def receive_message(self, attribute_names=None, max_message_cnt=1):
        if attribute_names is None:
            attribute_names = []
        return self.sqs_client.receive_message(QueueUrl=self.queue_url,
                                               AttributeNames=attribute_names,
                                               MaxNumberOfMessages=max_message_cnt)

    def delete_message(self, message):
        self.sqs_client.delete_message(QueueUrl=self.queue_url,
                                       ReceiptHandle=message['ReceiptHandle'])

    def send_message(self, message_body):
        return self.sqs_client.send_message(QueueUrl=self.queue_url,
                                            MessageBody=message_body)
