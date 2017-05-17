"""
The API Version
"""

from flask_restful import Resource

class Version(Resource):
    """
    Version resource
    """

    @classmethod
    def get(cls):
        """
        Gets the Version resource
        """

        return {"version": "0.0.1"}
