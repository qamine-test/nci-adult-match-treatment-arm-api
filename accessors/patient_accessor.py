"""
Patient MongoDB Accessor
"""

from accessors.mongo_db_accessor import MongoDbAccessor
from bson import json_util
import json
import logging

class PatientAccessor(MongoDbAccessor):
    """
    The Patient data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'patient')
        self.logger = logging.getLogger(__name__)

    def find(self, query, projection):
        """
        Returns items from the collection using a query and a projection
        """
        self.logger.debug('Retrieving Patients from database')
        return [json.loads(json_util.dumps(doc)) for doc in self.collection.find(query, projection)]

    def find_one(self, query, projection):
        """
        Returns one element found by filter
        """
        self.logger.debug('Retrieving one Patient from database')
        return json.loads(json_util.dumps(
            self.collection.find_one(query, projection)))
