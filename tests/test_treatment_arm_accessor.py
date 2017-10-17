#!/usr/bin/env python3

import datetime
import unittest

from bson import ObjectId
from ddt import ddt, data, unpack
from mock import patch

from accessors.treatment_arm_accessor import TreatmentArmsAccessor

DB = 'my_db'
URI = 'my_uri'
COLL_NAME = 'treatmentArms'


@ddt
class TreatmentArmAccessorTests(unittest.TestCase):
    def setUp(self):
        mongo_db_patcher = patch('accessors.mongo_db_accessor.MongoClient')
        self.addCleanup(mongo_db_patcher.stop)
        self.mock_mongo_client = mongo_db_patcher.start()
        self.mock_collection = self.mock_mongo_client.return_value[DB][COLL_NAME]

        logging_patcher = patch('accessors.treatment_arm_accessor.logging')
        self.addCleanup(logging_patcher.stop)
        self.mock_logger = logging_patcher.start().getLogger()

        env_patcher = patch('accessors.mongo_db_accessor.Environment')
        self.addCleanup(env_patcher.stop)
        self.mock_env = env_patcher.start().return_value
        self.mock_env.mongodb_uri = URI
        self.mock_env.db_name = DB

    # Test the TreatmentArmsAccessor constructor
    def test_init(self):
        """
        Simply verify the constructor does what it is supposed to do.
        """

        treatment_arms_accessor = TreatmentArmsAccessor()

        self.assertEqual(treatment_arms_accessor.collection_name, COLL_NAME)
        self.assertEqual(treatment_arms_accessor.db_name, DB)
        self.assertEqual(treatment_arms_accessor.mongo_client, self.mock_mongo_client.return_value)
        self.assertEqual(treatment_arms_accessor.database, self.mock_mongo_client.return_value[DB])
        self.assertEqual(treatment_arms_accessor.collection, self.mock_collection)
        self.assertEqual(treatment_arms_accessor.logger, self.mock_logger)
        self.mock_mongo_client.assert_called_once_with(URI)

    # Test the TreatmentArmsAccessor.get_ta_non_hotspot_rules method
    @data(
        ([], ),
        ([{'currentPatientStatus': 'ON_ARM'},{'currentPatientStatus': 'ON_ARM'}], ),
    )
    @unpack
    def test_get_ta_non_hotspot_rules(self, mock_documents):
        treatment_arms_accessor = TreatmentArmsAccessor()
        self.mock_collection.aggregate.return_value = mock_documents

        exp_result = [TreatmentArmsAccessor.mongo_to_python(doc) for doc in mock_documents]

        result = treatment_arms_accessor.get_ta_non_hotspot_rules()
        self.assertEqual(result, exp_result)
        self.mock_collection.aggregate.assert_called_once_with(TreatmentArmsAccessor.NON_HOTSPOT_RULES_PIPELINE)



if __name__ == '__main__':
    unittest.main()
