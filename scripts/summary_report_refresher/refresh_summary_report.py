#!/usr/bin/env python3

import logging
import os
from flask import Flask
from flask_env import MetaFlaskEnv

from config import log  # contains required log configuration; ignore Codacy complaints about unused code
from scripts.summary_report_refresher.refresher import Refresher


class Configuration(metaclass=MetaFlaskEnv):
    """
    Service configuration
    """
    DEBUG = True
    PORT = 5010
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/match')
    # Some instances of the DB are named 'Match' and others 'match'.
    DB_NAME = 'match' if '/match' in MONGODB_URI else 'Match'


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
