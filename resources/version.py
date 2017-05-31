"""
The API Version
"""

import logging

import flask
from flask_restful import Resource


class Version(Resource):
    """
    Version resource
    """
    def __init__(self, filename='version.json'):
        self.logger = logging.getLogger(__name__)
        self.filename = filename

    def get(self):
        """
        Gets the Version resource
        """
        self.logger.debug('Retrieving API Version')

        try:
            with flask.current_app.open_resource(self.filename) as f:
                json_data = flask.json.load(f)
                return json_data

        except Exception as ex:
            message = str(ex)
            self.logger.exception(message)
            return {"version": "0.0.2", "build_number": "None"}
