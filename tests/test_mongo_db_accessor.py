#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack
from mock import patch
from accessors.mongo_db_accessor import MongoDbAccessor
import datetime
from bson import ObjectId

DB = 'my_db'

URI = 'my_uri'

COLL_NAME = 'my_coll_name'


@ddt
class MongoDbAccessorTest(unittest.TestCase):
    def setUp(self):
        mongo_db_patcher = patch('accessors.mongo_db_accessor.MongoClient')
        self.addCleanup(mongo_db_patcher.stop)
        self.mock_mongo_client = mongo_db_patcher.start()
        self.mock_collection = self.mock_mongo_client.return_value[DB][COLL_NAME]

        logging_patcher = patch('accessors.mongo_db_accessor.logging')
        self.addCleanup(logging_patcher.stop)
        self.mock_logger = logging_patcher.start().getLogger()

        env_patcher = patch('accessors.mongo_db_accessor.Environment')
        self.addCleanup(env_patcher.stop)
        self.mock_env = env_patcher.start().return_value
        self.mock_env.mongodb_uri = URI
        self.mock_env.db_name = DB

    # Test the MongoDbAccessor constructor
    def test_init(self):
        """
        Simply verify the constructor does what it is supposed to do.
        """

        mongo_db_accessor = MongoDbAccessor(COLL_NAME, self.mock_logger)

        self.assertEqual(mongo_db_accessor.collection_name, COLL_NAME)
        self.assertEqual(mongo_db_accessor.db_name, DB)
        self.assertEqual(mongo_db_accessor.mongo_client, self.mock_mongo_client.return_value)
        self.assertEqual(mongo_db_accessor.database, self.mock_mongo_client.return_value[DB])
        self.assertEqual(mongo_db_accessor.collection, self.mock_collection)
        self.assertEqual(mongo_db_accessor.logger, self.mock_logger)
        self.mock_mongo_client.assert_called_once_with(URI)

    # Test the MongoDbAccessor.mongo_to_python method
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

    # Test the MongoDbAccessor.find method
    @data(
        ({}, {}, []),
        ({'currentPatientStatus': 'ON_ARM'}, {'currentPatientStatus': 1},
         [{'currentPatientStatus': 'ON_ARM'},{'currentPatientStatus': 'ON_ARM'}]),
    )
    @unpack
    def test_find(self, query, projection, mock_documents):
        mongo_db_accessor = MongoDbAccessor(COLL_NAME, self.mock_logger)
        self.mock_collection.find.return_value = mock_documents

        exp_result = [MongoDbAccessor.mongo_to_python(doc) for doc in mock_documents]

        result = mongo_db_accessor.find(query, projection)
        self.assertEqual(result, exp_result)
        self.mock_collection.find.assert_called_once_with(query, projection)

    # Test the MongoDbAccessor.find_one method
    @data(
        ({}, {}, None),
        ({'currentPatientStatus': 'ON_ARM'}, {'currentPatientStatus': 1}, {'currentPatientStatus': 'ON_ARM'}),
    )
    @unpack
    def test_find_one(self, query, projection, mock_document):
        mongo_db_accessor = MongoDbAccessor(COLL_NAME, self.mock_logger)
        self.mock_collection.find_one.return_value = mock_document

        exp_result = MongoDbAccessor.mongo_to_python(mock_document)

        result = mongo_db_accessor.find_one(query, projection)
        self.assertEqual(result, exp_result)
        self.mock_collection.find_one.assert_called_once_with(query, projection)

    # Test the MongoDbAccessor.count method
    @data(
        ({}, 0),
        ({'currentPatientStatus': 'ON_ARM'}, 6511),
    )
    @unpack
    def test_count(self, query, mock_count):
        mongo_db_accessor = MongoDbAccessor(COLL_NAME, self.mock_logger)
        self.mock_collection.count.return_value = mock_count

        exp_result = mock_count

        result = mongo_db_accessor.count(query)
        self.assertEqual(result, exp_result)
        self.mock_collection.count.assert_called_once_with(query)


if __name__ == '__main__':
    unittest.main()
