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
from threading import Thread

from scripts.ta_message_manager.ta_message_manager import TreatmentArmMessageManager

from config import flask_config
from config import log
from helpers.environment import Environment
from resources.amois import AmoisResource
from resources.amois import IsAmoisResource
from resources.healthcheck import HealthCheck
from resources.treatment_arm import TreatmentArms
from resources.treatment_arm import TreatmentArmsById
from resources.treatment_arm import TreatmentArmsOverview
from resources.version import Version

# Logging functionality
log.log_config()  # set the global logging configuration
# LOGGER = logging.getLogger(__name__)


def _initialize_error_handlers(application):
    from common.errors import ERRORS
    application.register_blueprint(ERRORS)


APP = Flask(__name__)
APP.config.from_object(flask_config.Configuration)
_initialize_error_handlers(APP)
API = Api(APP)

# Very important for development as this stands for Cross Origin Resource sharing. Essentially this is what allows for
# the UI to be run on the same box as this middleware piece of code. Consider this code boiler plate.
CORS = CORS(APP, resources={r"/api/*": {"origins": "*"}})


@APP.errorhandler(500)
def internal_server_error(error):
    logging.getLogger(__name__).exception(error)
    return str(error), 500


@APP.errorhandler(Exception)
def unhandled_exception(e):
    logging.getLogger(__name__).exception(e)
    return str(e), 500


API.add_resource(AmoisResource, '/api/v1/treatment_arms/amois')
API.add_resource(IsAmoisResource, '/api/v1/treatment_arms/is_amoi')
API.add_resource(HealthCheck, '/api/v1/treatment_arms/healthcheck', '/api/v1/treatment_arms/health_check')
API.add_resource(TreatmentArms, '/api/v1/treatment_arms', endpoint='get_all')
API.add_resource(TreatmentArmsById, '/api/v1/treatment_arms/<string:arm_id>', endpoint='get_by_id')
API.add_resource(TreatmentArmsOverview, '/api/v1/treatment_arms/dashboard/overview')
API.add_resource(Version, '/api/v1/treatment_arms/version', endpoint='get_version')


def run_api_server():
    log.log_config(Environment().logger_level)
    port = Environment().port
    logging.getLogger(__name__).debug("server starting on port :" + str(port))
    HTTP_SERVER = HTTPServer(WSGIContainer(APP))
    HTTP_SERVER.listen(port=port)
    IOLoop.instance().start()


def run_message_manager():
    log.log_config(Environment().logger_level)
    logging.getLogger(__name__).info("Starting the Treatment Arm API Message Queue")
    TreatmentArmMessageManager().run()
    logging.getLogger(__name__).info("Exiting the Treatment Arm API Message Queue")


if __name__ == '__main__':
    api = Thread(target=run_api_server)
    mm = Thread(target=run_message_manager)
    mm.setDaemon(True)

    api.start()
    mm.start()

    # api.join()
    # mm.join()

# if __name__ == '__main__':
#     port = Environment().port
#     LOGGER.debug("server starting on port :" + str(port))
#     HTTP_SERVER = HTTPServer(WSGIContainer(APP))
#     HTTP_SERVER.listen(port=port)
#     IOLoop.instance().start()
