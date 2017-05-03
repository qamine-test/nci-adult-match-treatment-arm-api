"""
The API Version
"""

from flask_restful import Resource
from flask.json import jsonify

class Version(Resource):
    """
    Version resource
    """

    @classmethod
    def get(cls):
        """
        Gets the Version resource
        """

        return jsonify({"version": "0.0.1"})
