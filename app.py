"""
Main application module
"""

#!/usr/bin/env python3

import logging
import os
# from logging.config import fileConfig

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from flask_env import MetaFlaskEnv

# from resources.amois import AmoisAnnotator
from resources.healthcheck import HealthCheck
from resources.version import Version
from resources.treatment_arm import TreatmentArms
from resources.treatment_arm import TreatmentArmsById
# from resources.treatment_arm import TreatmentArm


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
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())

APP = Flask(__name__)
APP.config.from_object(Configuration)

API = Api(APP)
CORS = CORS(APP, resources={r"/api/*": {"origins": "*"}})

# API.add_resource(AmoisAnnotator, '/api/v1/treatment_arms/amois', endpoint='get_amois')
API.add_resource(HealthCheck, '/api/v1/treatment_arms/healthcheck', endpoint='get_healthcheck')
API.add_resource(TreatmentArms, '/api/v1/treatment_arms', endpoint='get_all')
API.add_resource(TreatmentArmsById, '/api/v1/treatment_arms/<string:arm_id>', endpoint='get_by_id')
API.add_resource(Version, '/api/v1/treatment_arms/version', endpoint='get_version')

# API.add_resource(TreatmentArm,
#                  '/api/v1/treatment_arms/<string:name>/<string:version>',
#                  endpoint='get_one')
#

if __name__ == '__main__':
    # LOGGER.debug("connecting to '%s' on '%s'" % (Configuration.DB_NAME, Configuration.MONGODB_URI))
    LOGGER.debug("server starting on port :" + str(APP.config["PORT"]))
    HTTP_SERVER = HTTPServer(WSGIContainer(APP))
    HTTP_SERVER.listen(port=APP.config["PORT"])
    IOLoop.instance().start()
