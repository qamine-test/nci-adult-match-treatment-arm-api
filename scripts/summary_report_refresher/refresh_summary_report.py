#!/usr/bin/env python3
"""
A script to run the Summary Report Refresh process manually.
The primary use of this script is for development.  (Ordinarily, it will be executed via SQS message.)
"""
import logging

# from flask import Flask
#
# from config.flask_config import Configuration
from config import log
from scripts.summary_report_refresher.refresher import Refresher

# Logging functionality
log.log_config()
LOGGER = logging.getLogger(__name__)

# APP = Flask(__name__)
# APP.config.from_object(Configuration)
#

if __name__ == '__main__':
    LOGGER.info("Starting the Summary Report Refresher")

    exit_code = 0
    try:
        # with APP.app_context():
        r = Refresher()
        r.run()
    except Exception as exc:
        LOGGER.exception(str(exc))
        exit_code = 1

    LOGGER.info("Summary Report Refresher completed with exit code {}".format(exit_code))
    exit(exit_code)
