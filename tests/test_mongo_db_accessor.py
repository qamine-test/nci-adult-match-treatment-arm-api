#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack
from mock import patch
from accessors.mongo_db_accessor import MongoDbAccessor
import datetime
from bson import ObjectId

@ddt
class MongoDbAccessorTest(unittest.TestCase):
    def setUp(self):
        mongo_db_patcher = patch('accessors.mongo_db_accessor.MongoClient')
        self.addCleanup(mongo_db_patcher.stop)
        self.mock_mongo_client = mongo_db_patcher.start()

    @data(
        ('my_coll_name', 'my_uri', 'my_db'),
    )
    @unpack
    @patch('accessors.mongo_db_accessor.logging.getLogger')
    @patch('accessors.mongo_db_accessor.Environment')
    def test_init(self, collection_name, uri, db, mock_env, mock_logger):
        """
        Simply verify the contructor does what it is supposed to
        :param collection_name: a fake collection name for the test
        :param uri: a fake URI for the test
        :param db: a fake database name for the test
        :param mock_env: mocked Environment class that will contain the URI and database name
        """
        env_inst = mock_env.return_value
        env_inst.mongodb_uri = uri
        env_inst.db_name = db

        mongo_db_accessor = MongoDbAccessor(collection_name, mock_logger)

        self.assertEqual(mongo_db_accessor.collection_name, collection_name)
        self.assertEqual(mongo_db_accessor.db_name, db)
        self.assertEqual(mongo_db_accessor.mongo_client, self.mock_mongo_client.return_value)
        self.assertEqual(mongo_db_accessor.database, self.mock_mongo_client.return_value[db])
        self.assertEqual(mongo_db_accessor.collection, self.mock_mongo_client.return_value[db][collection_name])
        self.assertEqual(mongo_db_accessor.logger, mock_logger)
        self.mock_mongo_client.assert_called_once_with(uri)

    @data(
        ({}, {}),
        ({'_id': ObjectId('5600930b00924121fd9297c9'),
          'currentPatientStatus': 'OFF_TRIAL_NO_TA_AVAILABLE',
          'patientSequenceNumber': '10176',
          'registrationDate': datetime.datetime(2015, 9, 21, 23, 17, 46)},
         {'_id': {'$oid': '5600930b00924121fd9297c9'},
          'currentPatientStatus': 'OFF_TRIAL_NO_TA_AVAILABLE',
          'patientSequenceNumber': '10176',
          'registrationDate': {'$date': 1442877466000}})
    )
    @unpack
    def test_mongo_to_python(self, orig_doc, exp_doc):
        converted_doc = MongoDbAccessor.mongo_to_python(orig_doc)
        self.assertEqual(converted_doc, exp_doc)



if __name__ == '__main__':
    unittest.main()
