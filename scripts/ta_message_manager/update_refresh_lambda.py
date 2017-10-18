#!/usr/bin/env python3

import os
import pprint
import zipfile
from io import BytesIO

import boto3

from helpers.environment import Environment

try:
    # Zip up the code for the lambda function in memory
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as lambda_zip:
        lambda_function_script = 'scripts/ta_message_manager/send_refresh_message.py'
        lambda_zip.write(os.path.abspath(lambda_function_script), os.path.basename(lambda_function_script))
    buffer.seek(0)
    zip_data = buffer.read()

    # Send the zipped function to AWS
    client = boto3.client('lambda', region_name=Environment().region)
    response = client.update_function_code(
        FunctionName='SendSummaryReportRefreshMessage',
        Publish=True,
        ZipFile=zip_data,
    )

    print("SUCCESS!  Summary Report Refresh Lambda function has been updated.\nThis does not necessarily mean "
          "that the function works; that still needs to be tested.\n\nThe response from the update:")
    pprint.pprint(response)
except Exception as e:
    print("An exception prevented the successful upload of the new Lambda function:\n\n{}\n".format(str(e)))
    exit(16)
