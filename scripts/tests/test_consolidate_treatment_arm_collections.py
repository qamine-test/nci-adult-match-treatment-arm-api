#!/usr/bin/env python3

import datetime
import unittest

from ddt import ddt, data, unpack
from mock import patch

from scripts.consolidate_treatment_arm_collections import consolidate_treatment_arm_collections as ctac
import uuid

SCRIPT_PATH = 'scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections'

@ddt
class TestConsolidateTreatmentArmCollections(unittest.TestCase):

    # Test the TAConverter().convert function that converts a treatmentArm document to a treatmentArms document.
    @data(
        # successful conversion
        ({'_class': 'gov.match.model.TreatmentArm',
          '_id': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 2, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-03-31'},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentArmId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 2, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-03-31',
          'studyType': ['STANDARD'],
          'summaryReport': ctac.TAConverter.EMPTY_SUMMARY_REPORT,
          'dateArchived': None}),
        # successful conversion when input record has incorrect _class
        ({'_class': 'gov.match.model.TreatmentArmor',
          '_id': 'EAY131-U',
          'dateCreated': datetime.datetime(2016, 6, 7, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentArmId': 'EAY131-U',
          'dateCreated': datetime.datetime(2016, 6, 7, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31',
          'studyType': ['STANDARD', 'OUTSIDE_ASSAY'],
          'summaryReport': ctac.TAConverter.EMPTY_SUMMARY_REPORT,
          'dateArchived': None}),
        # 1. exception for missing _id
        ({'_class': 'gov.match.model.TreatmentArm',
          'dateCreated': datetime.datetime(2016, 6, 5, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER1 Amplification',
          'version': '2016-07-31'},
         'Invalid treatmentArm document'),
        # 2. exception for passing in already converted record
        ({'_class': 'gov.match.model.TreatmentArm',
          'treatmentArmId': 'EAY131-V',
          'dateCreated': datetime.datetime(2016, 6, 8, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER3 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 3. exception for input record's _id is None
        ({'_class': 'gov.match.model.TreatmentArm',
          '_id': None,
          'dateCreated': datetime.datetime(2016, 6, 9, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-03-31'},
         'Invalid treatmentArm document'),
        # 4. exception for ta_doc is None
        (None,
         'Invalid treatmentArm document'
         ),
    )
    @unpack
    @patch(SCRIPT_PATH + '.uuid')
    def test_TAConverter_convert(self, ta_doc, exp_result, mock_uuid):
        uuid_string = '0de86534-4791-41ce-bd5a-44fad51caa66'
        mock_uuid.uuid4.return_value = uuid.UUID(uuid_string)

        try:
            ret_doc = ctac.TAConverter().convert(ta_doc)
            exp_result_with_state_token = dict(**exp_result, **{'stateToken': uuid_string})
            self.assertEqual(ret_doc, exp_result_with_state_token)
        except Exception as e:
            self.assertEqual(str(e), exp_result)

    # Test the TAHConverter().convert function that converts a treatmentArmHistory document to a treatmentArms document.
    DEFAULT_TA_DRUGS = [{'drugId': '763093', 'name': 'Trametinib dimethyl sulfoxide (GSK1120212B)', 'pathway': 'NF1'}]
    DEFAULT_TA_FROM_TA_HISTORY = {
        '_id': 'EAY131-S1',
        'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
        'name': 'Trametinib in NF1 mutation',
        'treatmentArmDrugs': DEFAULT_TA_DRUGS,
        'version': '09-14-2015'}

    TA_HISTORY_TA1 = {'_id': 'EAY131-S1',
                      'dateCreated': datetime.datetime(2015, 1, 13, 21, 8, 22, 83000),
                      'name': 'Trametinib in NF1 mutation',
                      'treatmentArmDrugs': DEFAULT_TA_DRUGS,
                      'version': '09-14-2015'}

    TA_HISTORY_TA2 = {'_id': 'EAY131-S1',
                      'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                      'name': 'Trametinib in NF1 mutation',
                      'treatmentArmDrugs': DEFAULT_TA_DRUGS,
                      'version': '09-14-2016'}

    TA_HISTORY_DOC1 = {'_class': 'gov.match.model.TreatmentArmHistoryItem',
                       '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
                       'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
                       'treatmentArm': TA_HISTORY_TA1}

    TA_HISTORY_DOC2 = {'_class': 'gov.match.model.TreatmentArmHistoryItem',
                       '_id': '4300d834-4234-44e3-acdf-65b4a3c444b1',
                       'dateArchived': datetime.datetime(2016, 12, 5, 7, 36, 20, 602000),
                       'treatmentArm': TA_HISTORY_TA2}

    TA_DOC1 = {'_class': 'gov.match.model.TreatmentArm',
               '_id': 'EAY131-Z1',
               'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 707000),
               'name': 'TDM1 in HER2 Amplification',
               'version': '2016-07-30'}

    TA_DOC2 = {'_class': 'gov.match.model.TreatmentArm',
               '_id': 'EAY131-Q',
               'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 708000),
               'name': 'TDM2 in HER2 Amplification',
               'version': '2016-05-30'}

    TA_DOC3 = {'_class': 'gov.match.model.TreatmentArm',
               '_id': 'EAY131-Z',
               'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 709000),
               'name': 'TDM3 in HER2 Amplification',
               'version': '2016-12-30'}

    @data(
        # successful conversion
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': DEFAULT_TA_FROM_TA_HISTORY},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentArmId': 'EAY131-S1',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
          'name': 'Trametinib in NF1 mutation',
          'studyType': ['STANDARD'],
          'treatmentArmDrugs': DEFAULT_TA_DRUGS,
          'version': '09-14-2015'}
         ),
        # 1. exception for missing _id
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          'dateArchived': datetime.datetime(2016, 1, 16, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': DEFAULT_TA_FROM_TA_HISTORY},
         'Invalid treatmentArmHistory document'
         ),
        # 2. exception for unpopulated _id
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': None,
          'dateArchived': datetime.datetime(2016, 1, 17, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': DEFAULT_TA_FROM_TA_HISTORY},
         'Invalid treatmentArmHistory document'
         ),
        # 3. exception for missing dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'exclusionCriterias': [],
          'treatmentArm': DEFAULT_TA_FROM_TA_HISTORY},
         'Invalid treatmentArmHistory document'
         ),
        # 4. exception for unpopulated dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': None,
          'exclusionCriterias': [],
          'treatmentArm': DEFAULT_TA_FROM_TA_HISTORY},
         'Invalid treatmentArmHistory document'
         ),
        # 5. exception for missing treatmentArm
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 603000),
          'exclusionCriterias': [],
          },
         'Invalid treatmentArmHistory document'
         ),
        # 6. exception for unpopulated treatmentArm[_id]
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444b1',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 604000),
          'exclusionCriterias': [],
          'treatmentArm': {'_id': None,
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': DEFAULT_TA_DRUGS,
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 7. exception for missing treatmentArm[_id]
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 606000),
          'exclusionCriterias': [],
          'treatmentArm': {'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': DEFAULT_TA_DRUGS,
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 8. exception for tah_doc is None
        (None,
         'Invalid treatmentArmHistory document'
         ),
    )
    @unpack
    @patch(SCRIPT_PATH + '.uuid')
    def test_TAHConverter_convert(self, tah_doc, exp_result, mock_uuid):
        uuid_string = '0de86534-4791-41ce-bd5a-44fad51caa88'
        mock_uuid.uuid4.return_value = uuid.UUID(uuid_string)

        try:
            ret_doc = ctac.TAHConverter().convert(tah_doc)
            self.assertTrue('summaryReport' not in ret_doc)
            exp_result_with_state_token = dict(**exp_result, **{'stateToken': uuid_string})
            self.assertEqual(ret_doc, exp_result_with_state_token)
        except Exception as e:
            self.assertEqual(str(e), exp_result)

    def test_TAConverter_collection_name(self):
        self.assertEqual(ctac.TAConverter().get_collection_name(), "treatmentArm")

    def test_TAHConverter_collection_name(self):
        self.assertEqual(ctac.TAHConverter().get_collection_name(), "treatmentArmHistory")

    @data([TA_DOC1, TA_DOC2, TA_DOC3])
    @patch(SCRIPT_PATH + '.LOGGER')
    @patch(SCRIPT_PATH + '.MongoDbAccessor')
    def test_convert_to_treatment_arms(self, indata, mock_db_accessor, mock_logger):
        mock_db_accessor.get_documents = lambda n: indata
        cnt = ctac.convert_to_treatment_arms(mock_db_accessor, ctac.TAConverter())
        self.assertEqual(cnt, len(indata))

        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()

    @data([82], [0])
    @unpack
    @patch(SCRIPT_PATH + '.LOGGER')
    @patch(SCRIPT_PATH + '.MongoDbAccessor')
    def test_prepare_treatment_arms_collection(self, initial_doc_cnt, mock_db_accessor, mock_logger):
        mock_db_accessor.get_document_count = lambda n: initial_doc_cnt

        def mock_clear():
            mock_db_accessor.get_document_count = lambda n: 0
        mock_db_accessor.clear_treatment_arms = mock_clear

        cnt = ctac.prepare_treatment_arms_collection(mock_db_accessor)
        self.assertEqual(cnt, 0)

        if initial_doc_cnt != 0:
            mock_logger.info.assert_called()

    @data(
        # 1. Expected normal execution: both tables contain data with no errors
        ([TA_DOC1, TA_DOC2, TA_DOC3], # treatmentArm data
         [TA_HISTORY_DOC1, TA_HISTORY_DOC2],  # treatmentArmHistory data
         0  # expected return value
        ),
        # 2. test when both source tables are empty
        ([], [], 0),
        # 3. test when treatmentArm contains data and treatmentArmHistory does not
        ([TA_DOC1, TA_DOC2, TA_DOC3], # treatmentArm data
         [],  # treatmentArmHistory data is empty
         0  # expected return value
        ),
        # 4. test when treatmentArmHistory contains data and treatmentArm does not
        ([],  # treatmentArm data is empty
         [TA_HISTORY_DOC1, TA_HISTORY_DOC2],  # treatmentArmHistory data
         0  # expected return value
        ),
        # 5. Test when an exception occurs
        ([  # treatmentArm data with missing _id in second record
             TA_DOC1,
             {'_class': 'gov.match.model.TreatmentArm',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-05-31'},
             TA_DOC3
         ],
         [TA_HISTORY_DOC1, TA_HISTORY_DOC2],  # treatmentArmHistory data
         -1  # expected return value for error
        )
    )
    @unpack
    @patch(SCRIPT_PATH + '.LOGGER')
    @patch(SCRIPT_PATH + '.MongoDbAccessor')
    def test_main(self, ta_data, tah_data, exp_ret_val, mock_db_accessor, mock_logger):
        mock_db_accessor.get_documents = lambda n: ta_data if n == 'treatmentArm' else tah_data
        mock_db_accessor.get_document_count = lambda n: 0
        ret_val = ctac.main(mock_db_accessor)
        self.assertEqual(ret_val, exp_ret_val)
        mock_logger.info.assert_called()
        if ret_val != 0:
            mock_logger.exception.assert_called_once()


    # Test the get_mongo_accessor() function
    @data(
        ({}, ctac.LOCAL_DB_DEBUG_LOG_MSG),
        ({'MONGODB_URI': 'mongodb://www.abcdefg.com/Match'}, ctac.ENV_VAR_DEBUG_LOG_MSG),
    )
    @unpack
    @patch(SCRIPT_PATH + '.os')
    @patch(SCRIPT_PATH + '.LOGGER')
    @patch(SCRIPT_PATH + '.MongoDbAccessor')
    def test_get_mongo_accessor(self, env_dict, exp_log_msg, mock_db_accessor, mock_logger, mock_os):
        mock_os.environ = env_dict

        db_accessor = ctac.get_mongo_accessor()

        mock_logger.debug.assert_called_with(exp_log_msg)
        self.assertIs(db_accessor, mock_db_accessor.return_value)

if __name__ == '__main__':
    unittest.main()
