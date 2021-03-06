#!/usr/bin/env python3
"""
A unit test script for the accessors/treatment_arm_accessor.py module.
"""

import unittest

from bson import ObjectId
from ddt import ddt, data, unpack
from mock import patch, Mock

from accessors.treatment_arm_accessor import TreatmentArmsAccessor

DB = 'my_db'
URI = 'my_uri'
COLL_NAME = 'treatmentArms'


@ddt
class TreatmentArmAccessorTests(unittest.TestCase):
    # Constants used in the test of the TreatmentArmsAccessor.get_ta_identifier_rules method:
    SNV_IDENTIFIER_RULES_PIPELINE = TreatmentArmsAccessor._create_identifier_rules_pipeline('singleNucleotideVariants')
    CNV_IDENTIFIER_RULES_PIPELINE = TreatmentArmsAccessor._create_identifier_rules_pipeline('copyNumberVariants')
    GENE_FUSION_IDENTIFIER_RULES_PIPELINE = TreatmentArmsAccessor._create_identifier_rules_pipeline('geneFusions')
    INDEL_IDENTIFIER_RULES_PIPELINE = TreatmentArmsAccessor._create_identifier_rules_pipeline('indels')

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
        self.mock_collection.aggregate.return_value = mock_documents

        exp_result = [TreatmentArmsAccessor.mongo_to_python(doc) for doc in mock_documents]

        result = TreatmentArmsAccessor().get_ta_non_hotspot_rules()
        self.assertEqual(result, exp_result)
        self.mock_collection.aggregate.assert_called_once_with(TreatmentArmsAccessor.NON_HOTSPOT_RULES_PIPELINE)

    # Test the TreatmentArmsAccessor.get_ta_identifier_rules method
    @data(
        ('singleNucleotideVariants', SNV_IDENTIFIER_RULES_PIPELINE),
        ('copyNumberVariants', CNV_IDENTIFIER_RULES_PIPELINE),
        ('geneFusions', GENE_FUSION_IDENTIFIER_RULES_PIPELINE),
        ('indels', INDEL_IDENTIFIER_RULES_PIPELINE),
        ('INVALID_VAR_TYPE', Exception("Unknown variant_type 'INVALID_VAR_TYPE' passed to TreatmentArmsAccessor")),
    )
    @unpack
    def test_get_ta_identifier_rules(self, variant_type, exp_pipeline):
        treatment_arms_accessor = TreatmentArmsAccessor()

        if isinstance(exp_pipeline, Exception):
            with self.assertRaises(Exception) as cm:
                treatment_arms_accessor.get_ta_identifier_rules(variant_type)
            self.assertEqual(str(cm.exception), str(exp_pipeline))
        else:
            mock_documents = [{'doc_num': 1}, {'doc_num': 2}]
            self.mock_collection.aggregate.return_value = mock_documents

            exp_result = [TreatmentArmsAccessor.mongo_to_python(doc) for doc in mock_documents]

            result = treatment_arms_accessor.get_ta_identifier_rules(variant_type)
            self.assertEqual(result, exp_result)
            self.mock_collection.aggregate.assert_called_once_with(exp_pipeline)

    # Test the TreatmentArmsAccessor._create_identifier_rules_pipeline method
    @data(
        ('indels',
         [
             {"$match": {"variantReport.indels": {"$ne": []}}},
             {"$unwind": "$variantReport.indels"},
             {"$project": {"treatmentArmId": 1,
                           "version": 1,
                           "dateArchived": 1,
                           "treatmentArmStatus": 1,
                           "identifier": "$variantReport.indels.identifier",
                           "protein": "$variantReport.indels.protein",
                           "inclusion": "$variantReport.indels.inclusion",
                           "type": "Hotspot"
                           }}
         ]
         ),
        ('INVALID_VAR_TYPE', KeyError("INVALID_VAR_TYPE")),
    )
    @unpack
    def test_create_identifier_rules_pipeline(self, variant_type, exp_pipeline):
        if isinstance(exp_pipeline, KeyError):
            with self.assertRaises(KeyError) as cm:
                TreatmentArmsAccessor._create_identifier_rules_pipeline(variant_type)
            self.assertEqual(str(cm.exception), str(exp_pipeline))
        else:
            pipeline = TreatmentArmsAccessor._create_identifier_rules_pipeline(variant_type)
            self.assertEqual(pipeline, exp_pipeline)

    # Test the TreatmentArmsAccessor.get_arms_for_summary_report_refresh method
    def test_get_arms_for_summary_report_refresh(self):
        """
        A trivial test:  Only tests that the collection's find function is called with the correct parameters and
        that its return value is what is returned from TreatmentArmsAccessor.get_arms_for_summary_report_refresh.
        """
        mock_documents = [{'doc_num': 4}, {'doc_num': 6}]
        self.mock_collection.find.return_value = mock_documents

        exp_result = [TreatmentArmsAccessor.mongo_to_python(doc) for doc in mock_documents]

        result = TreatmentArmsAccessor().get_arms_for_summary_report_refresh()
        self.assertEqual(result, exp_result)
        self.mock_collection.find.assert_called_once_with(TreatmentArmsAccessor.SUMMARY_REPORT_REFRESH_QUERY,
                                                          TreatmentArmsAccessor.SUMMARY_REPORT_REFRESH_PROJECTION)

    # Test the TreatmentArmsAccessor.update_summary_report method
    @data(
        ({'$oid': '598386900e04839ba1fabcfa'}, 1, True),
        ({'$oid': '598386900e04839ba1fabcfa'}, 0, False),
    )
    @unpack
    def test_update_summary_report(self, ta_id, mocked_match_count, exp_result):
        mocked_update_result = Mock()
        mocked_update_result.matched_count = mocked_match_count
        self.mock_collection.update_one.return_value = mocked_update_result

        summary_report_json = {"sum1": 23, "sum2": 7}

        result = TreatmentArmsAccessor().update_summary_report(ta_id, summary_report_json)
        self.assertEqual(result, exp_result)
        self.mock_collection.update_one.assert_called_once_with({'_id': ObjectId(ta_id['$oid'])},
                                                                {'$set': {'summaryReport': summary_report_json}})

if __name__ == '__main__':
    unittest.main()
