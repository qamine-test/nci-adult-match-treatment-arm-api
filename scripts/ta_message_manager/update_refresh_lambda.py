#!/usr/bin/env python3

import pprint
import zipfile
from io import BytesIO

import boto3

from helpers.environment import Environment

# Zip up the code for the lambda function in memory
buffer = BytesIO()
with zipfile.ZipFile(buffer, 'w') as lambda_zip:
    lambda_zip.write('send_refresh_message.py')
buffer.seek(0)
zip_data = buffer.read()

# Send the zipped function to AWS
client = boto3.client('lambda', region_name=Environment().region)
response = client.update_function_code(
    FunctionName='SendSummaryReportRefreshMessage',
    Publish=True,
    ZipFile=zip_data,
)

pprint.pprint(response)
