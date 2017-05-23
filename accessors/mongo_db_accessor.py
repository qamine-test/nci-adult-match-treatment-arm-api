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
        host = flask.current_app.config["MONGO_HOST"]
        port = flask.current_app.config["MONGO_PORT"]
        db = 'match'

        uri = "mongodb://%s:%s/%s"%(host, port, db)

        self.mongo_client = MongoClient(uri)
        self.database = self.mongo_client[db]
        self.collection = self.database[collection_name]
