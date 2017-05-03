from accessors.mongo_db_accessor import MongoDbAccessor
from bson import json_util
import json


class TreatmentArmAccessor(MongoDbAccessor):
    """
    The TreatmentArm data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'treatmentArm')

    def find(self, query, projection):
        """
        Returns items from the collection using a query and a projection
        """

        res = []
        for doc in self.collection.find(query, projection):
            res.append(json.loads(json_util.dumps(doc)))

        return res

    def find_one(self, query, projection):
        """
        Returns one element found by filter
        """

        return json.loads(json_util.dumps(
            self.collection.find_one(query, projection)))
