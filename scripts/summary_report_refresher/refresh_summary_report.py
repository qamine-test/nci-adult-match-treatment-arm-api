#!/usr/bin/env python3

import logging
from flask import Flask

from config.flask_config import Configuration
from config import log  # contains required log configuration; ignore Codacy complaints about unused code
from scripts.summary_report_refresher.refresher import Refresher


# Logging functionality
LOGGER = logging.getLogger(__name__)

APP = Flask(__name__)
APP.config.from_object(Configuration)


if __name__ == '__main__':
    LOGGER.info("Starting the Summary Report Refresher")
    exit_code = 0
    try:
        with APP.app_context():
            Refresher().run()
    except Exception as exc:
        LOGGER.exception(str(exc))
        exit_code = 1

    exit(exit_code)
