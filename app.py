"""
Main application module
"""

#!/usr/bin/env python3

import logging

from flask import Flask
# from flask_cors import CORS
from flask_restful import Api
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from config import flask_config
from config import log
from helpers.environment import Environment
from resources.amois import AmoisResource
from resources.healthcheck import HealthCheck
from resources.treatment_arm import TreatmentArms
from resources.treatment_arm import TreatmentArmsById
from resources.treatment_arm import TreatmentArmsOverview
from resources.version import Version

# Logging functionality
log.log_config()  # set the global logging configuration
LOGGER = logging.getLogger(__name__)

APP = Flask(__name__)
APP.config.from_object(flask_config.Configuration)

API = Api(APP)
# cors = CORS(APP, resources={r"/api/*": {"origins": "*"}})

API.add_resource(AmoisResource, '/api/v1/treatment_arms/amois')
API.add_resource(HealthCheck, '/api/v1/treatment_arms/healthcheck', endpoint='get_healthcheck')
API.add_resource(TreatmentArms, '/api/v1/treatment_arms', endpoint='get_all')
API.add_resource(TreatmentArmsById, '/api/v1/treatment_arms/<string:arm_id>', endpoint='get_by_id')
API.add_resource(TreatmentArmsOverview, '/api/v1/treatment_arms/dashboard/overview')
API.add_resource(Version, '/api/v1/treatment_arms/version', endpoint='get_version')

if __name__ == '__main__':
    port = Environment().port
    LOGGER.debug("server starting on port :" + str(port))
    HTTP_SERVER = HTTPServer(WSGIContainer(APP))
    HTTP_SERVER.listen(port=port)
    IOLoop.instance().start()
