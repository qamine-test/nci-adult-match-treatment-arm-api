"""
Mongo DB connection helper
"""

from pymongo import MongoClient
import flask


class MongoDbAccessor(object):
    """
    Base class for MongoDB accessors
    """
    def __init__(self, collection_name):
        uri = flask.current_app.config["MONGODB_URI"]
        db = flask.current_app.config["DB_NAME"]

        self.mongo_client = MongoClient(uri)
        self.database = self.mongo_client[db]
        self.collection = self.database[collection_name]
