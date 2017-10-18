"""
This is an AWS Lambda function for putting a message on an SQS queue that tells the system it is
time to refresh the summary report data in the treatmentArms collection in the MongoDB Match database.

The event param should have an item named 'queue_name' that specifies the queue to which the message to be sent.
For example:
    {"queue_name": "treatment-arm-api-int-queue"}
"""
import boto3

REFRESH_MSG = "RefreshSummaryReport"


def lambda_handler(event, context):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName=event['queue_name'])
    return queue.send_message(MessageBody=REFRESH_MSG)
