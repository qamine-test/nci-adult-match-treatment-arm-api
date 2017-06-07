"""
Patient MongoDB Accessor
"""

import logging

from accessors.mongo_db_accessor import MongoDbAccessor


class PatientAccessor(MongoDbAccessor):
    """
    The Patient data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'patient')
        self.logger = logging.getLogger(__name__)

   def find(self, query, projection):
        """
        Returns items from the collection using a query and a projection.
        """
        self.logger.debug('Retrieving Patient documents from database')
        return MongoDbAccessor.find(self, query, projection)

    def find_one(self, query, projection):
        """
        Returns one element found by filter
        """
        self.logger.debug('Retrieving one Patient document from database')
        return MongoDbAccessor.find_one(self, query, projection)

    def count(self, query):
        """
        Returns the number of items from the collection using a query.
        """
        self.logger.debug('Counting Patient documents in database')
        return MongoDbAccessor.count(self, query)

    def aggregate(self, pipeline):
        """
        Returns the aggregation defined by pipeline.
        """
        self.logger.debug('Retrieving Patient document aggregation from database')
        return MongoDbAccessor.aggregate(self, pipeline)
