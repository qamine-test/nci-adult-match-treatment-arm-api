"""
Main application module
"""

#!/usr/bin/env python3

import logging

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from config.flask_config import Configuration
from config import log  # pylint: disable=unused-import
from resources.amois import AmoisResource
from resources.healthcheck import HealthCheck
from resources.treatment_arm import TreatmentArms
from resources.treatment_arm import TreatmentArmsById
from resources.version import Version


# Logging functionality
LOGGER = logging.getLogger(__name__)

APP = Flask(__name__)
APP.config.from_object(Configuration)

API = Api(APP)
CORS = CORS(APP, resources={r"/api/*": {"origins": "*"}})

API.add_resource(AmoisResource, '/api/v1/treatment_arms/amois')
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
