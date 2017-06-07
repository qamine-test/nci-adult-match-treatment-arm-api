"""
Mongo DB connection helper
"""
import json

import flask
from bson import json_util
from pymongo import MongoClient


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

    def find(self, query, projection):
        """
        Returns items from the collection using a query and a projection.
        """
        return [json.loads(json_util.dumps(doc)) for doc in self.collection.find(query, projection)]

    def find_one(self, query, projection):
        """
        Returns one element found by filter
        """
        return json.loads(json_util.dumps(self.collection.find_one(query, projection)))

    def count(self, query):
        """
        Returns the number of items from the collection using a query.
        """
        return self.collection.count(query)

    def aggregate(self, pipeline):
        """
        Returns the aggregation defined by pipeline.
        """
        return self.collection.aggregate(pipeline)
