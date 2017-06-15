#!/usr/bin/env python3

import datetime
import unittest

from ddt import ddt, data, unpack
from mock import patch

from scripts.consolidate_treatment_arm_collections import consolidate_treatment_arm_collections as ctac


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
          'version': '2016-05-31'},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 2, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31',
          'summaryReport': {
            'numCurrentPatientsOnArm': 0,
            'numFormerPatients': 0,
            'numPendingArmApproval': 0,
            'numNotEnrolledPatient': 0,
            'assignmentRecords': []
          },
          'dateArchived': None}),
        # successful conversion when input record has incorrect _class
        ({'_class': 'gov.match.model.TreatmentArmor',
          '_id': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 7, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 7, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31',
          'summaryReport': {
            'numCurrentPatientsOnArm': 0,
            'numFormerPatients': 0,
            'numPendingArmApproval': 0,
            'numNotEnrolledPatient': 0,
            'assignmentRecords': []
          },
          'dateArchived': None}),
        # 1. exception for missing _id
        ({'_class': 'gov.match.model.TreatmentArm',
          'dateCreated': datetime.datetime(2016, 6, 5, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 2. exception for passing in already converted record
        ({'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 8, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 3. exception for input record's _id is None
        ({'_class': 'gov.match.model.TreatmentArm',
          '_id': None,
          'dateCreated': datetime.datetime(2016, 6, 9, 14, 56, 52, 704000),
          'exclusionCriterias': [],
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 4. exception for ta_doc is None
        (None,
         'Invalid treatmentArm document'
         ),
    )
    @unpack
    def test_TAConverter_convert(self, ta_doc, exp_result):
        try:
            ret_doc = ctac.TAConverter().convert(ta_doc)
            self.assertTrue('stateToken' in ret_doc and ret_doc['stateToken'])
            del ret_doc['stateToken']  # stateToken is randomly generated so must be removed prior to next assertion
            self.assertEqual(ret_doc, exp_result)
        except Exception as e:
            self.assertEqual(str(e), exp_result)

    # Test the TAHConverter().convert function that converts a treatmentArmHistory document to a treatmentArms document.
    @data(
        # successful conversion
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': {'_id': 'EAY131-S1',
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763093',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK1120212B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-S1',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
          'name': 'Trametinib in NF1 mutation',
          'treatmentArmDrugs': [{'drugId': '763093',
                                 'name': 'Trametinib dimethyl sulfoxide (GSK1120212B)',
                                 'pathway': 'NF1'}],
          'version': '09-14-2015'}
         ),
        # 1. exception for missing _id
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          'dateArchived': datetime.datetime(2016, 1, 16, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': {'_id': 'EAY131-S1',
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763093',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK1120212B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 2. exception for unpopulated _id
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': None,
          'dateArchived': datetime.datetime(2016, 1, 17, 21, 36, 20, 602000),
          'exclusionCriterias': [],
          'treatmentArm': {'_id': 'EAY131-S1',
                           'dateCreated': datetime.datetime(2016, 1, 14, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763093',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK1120212B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 3. exception for missing dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'exclusionCriterias': [],
          'treatmentArm': {'_id': 'EAY131-S1',
                           'dateCreated': datetime.datetime(2016, 1, 15, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763091',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK112021B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 4. exception for unpopulated dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': None,
          'exclusionCriterias': [],
          'treatmentArm': {'_id': 'EAY131-S1',
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 84000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763092',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK112022B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
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
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 604000),
          'exclusionCriterias': [],
          'treatmentArm': {'_id': None,
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763094',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK112012B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 7. exception for missing treatmentArm[_id]
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 606000),
          'exclusionCriterias': [],
          'treatmentArm': {'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 84000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763095',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK120212B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 8. exception for tah_doc is None
        (None,
         'Invalid treatmentArmHistory document'
         ),
    )
    @unpack
    def test_TAHConverter_convert(self, tah_doc, exp_result):
        try:
            ret_doc = ctac.TAHConverter().convert(tah_doc)
            self.assertTrue('summaryReport' not in ret_doc)
            self.assertTrue('stateToken' in ret_doc and ret_doc['stateToken'])
            del ret_doc['stateToken']  # stateToken is randomly generated so must be removed prior to next assertion
            self.assertEqual(ret_doc, exp_result)
        except Exception as e:
            self.assertEqual(str(e), exp_result)

    def test_TAConverter_collection_name(self):
        self.assertEqual(ctac.TAConverter().get_collection_name(), "treatmentArm")

    def test_TAHConverter_collection_name(self):
        self.assertEqual(ctac.TAHConverter().get_collection_name(), "treatmentArmHistory")

    @data(
        # treatmentArm data
        ([{'_class': 'gov.match.model.TreatmentArm',
           '_id': 'EAY131-Z',
           'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
           'name': 'TDM1 in HER2 Amplification',
           'version': '2016-07-31'},
          {'_class': 'gov.match.model.TreatmentArm',
           '_id': 'EAY131-Q',
           'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 705000),
           'name': 'TDM1 in HER2 Amplification',
           'version': '2016-05-31'},
          {'_class': 'gov.match.model.TreatmentArm',
           '_id': 'EAY131-Z1',
           'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 706000),
           'name': 'TDM1 in HER2 Amplification',
           'version': '2016-12-31'}
          ]
         )
    )
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.LOGGER')
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.MongoDbAccessor')
    def test_convert_to_treatment_arms(self, indata, mock_db_accessor, mock_logger):
        mock_db_accessor.get_documents = lambda n: indata
        cnt = ctac.convert_to_treatment_arms(mock_db_accessor, ctac.TAConverter())
        self.assertEqual(cnt, len(indata))

        mock_logger.debug.assert_called()
        mock_logger.info.assert_called()

    @data([82], [0])
    @unpack
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.LOGGER')
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.MongoDbAccessor')
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
        ([  # treatmentArm data
            {'_class': 'gov.match.model.TreatmentArm',
             '_id': 'EAY131-Z',
             'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 707000),
             'name': 'TDM1 in HER2 Amplification',
             'version': '2016-07-30'},
            {'_class': 'gov.match.model.TreatmentArm',
             '_id': 'EAY131-Q',
             'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 708000),
             'name': 'TDM1 in HER2 Amplification',
             'version': '2016-05-30'},
            {'_class': 'gov.match.model.TreatmentArm',
             '_id': 'EAY131-Z1',
             'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 709000),
             'name': 'TDM1 in HER2 Amplification',
             'version': '2016-12-30'}
         ],
         [  # treatmentArmHistory data
            {'_class': 'gov.match.model.TreatmentArmHistoryItem',
             '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
             'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
             'treatmentArm': {'_id': 'EAY131-S1',
                              'dateCreated': datetime.datetime(2015, 1, 13, 21, 8, 22, 83000),
                              'name': 'Trametinib in NF1 mutation',
                              'treatmentArmDrugs': [{'drugId': '763093',
                                                     'name': 'Trametinib dimethyl '
                                                             'sulfoxide (GSK1120212B)',
                                                     'pathway': 'NF1'}],
                              'version': '09-14-2015'}},
            {'_class': 'gov.match.model.TreatmentArmHistoryItem',
             '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
             'dateArchived': datetime.datetime(2016, 12, 5, 7, 36, 20, 602000),
             'treatmentArm': {'_id': 'EAY131-S1',
                              'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                              'name': 'Trametinib in NF1 mutation',
                              'treatmentArmDrugs': [{'drugId': '763093',
                                                     'name': 'Trametinib dimethyl '
                                                             'sulfoxide (GSK1120212B)',
                                                     'pathway': 'NF1'}],
                              'version': '09-14-2016'}}
         ],
         0  # expected return value
        ),
        # 2. test when both source tables are empty
        ([], [], 0),
        # 3. test when treatmentArm contains data and treatmentArmHistory does not
        ([  # treatmentArm data
             {'_class': 'gov.match.model.TreatmentArm',
              '_id': 'EAY131-Z',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 724000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-07-31'},
             {'_class': 'gov.match.model.TreatmentArm',
              '_id': 'EAY131-Q',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 714000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-05-31'},
             {'_class': 'gov.match.model.TreatmentArm',
              '_id': 'EAY131-Z1',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 724000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-12-31'}
         ],
         [  # treatmentArmHistory data is empty
         ],
         0  # expected return value
        ),
        # 4. test when treatmentArmHistory contains data and treatmentArm does not
        ([  # treatmentArm data is empty
         ],
         [  # treatmentArmHistory data
             {'_class': 'gov.match.model.TreatmentArmHistoryItem',
              '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
              'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 612000),
              'treatmentArm': {'_id': 'EAY131-S1',
                               'dateCreated': datetime.datetime(2015, 1, 13, 21, 8, 22, 83000),
                               'name': 'Trametinib in NF1 mutation',
                               'treatmentArmDrugs': [{'drugId': '764093',
                                                      'name': 'Trametinib dimethyl '
                                                              'sulfoxide (GSK1120212B)',
                                                      'pathway': 'NF1'}],
                               'version': '09-14-2015'}},
             {'_class': 'gov.match.model.TreatmentArmHistoryItem',
              '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
              'dateArchived': datetime.datetime(2016, 12, 5, 7, 36, 20, 612000),
              'treatmentArm': {'_id': 'EAY131-S1',
                               'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                               'name': 'Trametinib in NF1 mutation',
                               'treatmentArmDrugs': [{'drugId': '764093',
                                                      'name': 'Trametinib dimethyl '
                                                              'sulfoxide (GSK1120212B)',
                                                      'pathway': 'NF1'}],
                               'version': '09-14-2016'}}
         ],
         0  # expected return value
        ),
        # 5. Test when an exception occurs
        ([  # treatmentArm data with missing _id in second record
             {'_class': 'gov.match.model.TreatmentArm',
              '_id': 'EAY131-Z',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-07-31'},
             {'_class': 'gov.match.model.TreatmentArm',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-05-31'},
             {'_class': 'gov.match.model.TreatmentArm',
              '_id': 'EAY131-Z1',
              'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
              'name': 'TDM1 in HER2 Amplification',
              'version': '2016-12-31'}
         ],
         [  # treatmentArmHistory data
             {'_class': 'gov.match.model.TreatmentArmHistoryItem',
              '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
              'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
              'treatmentArm': {'_id': 'EAY131-S1',
                               'dateCreated': datetime.datetime(2015, 1, 13, 21, 8, 22, 83000),
                               'name': 'Trametinib in NF1 mutation',
                               'treatmentArmDrugs': [{'drugId': '763093',
                                                      'name': 'Trametinib dimethyl '
                                                              'sulfoxide (GSK1120212B)',
                                                      'pathway': 'NF1'}],
                               'version': '09-14-2015'}},
             {'_class': 'gov.match.model.TreatmentArmHistoryItem',
              '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
              'dateArchived': datetime.datetime(2016, 12, 5, 7, 36, 20, 602000),
              'treatmentArm': {'_id': 'EAY131-S1',
                               'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                               'name': 'Trametinib in NF1 mutation',
                               'treatmentArmDrugs': [{'drugId': '763093',
                                                      'name': 'Trametinib dimethyl '
                                                              'sulfoxide (GSK1120212B)',
                                                      'pathway': 'NF1'}],
                               'version': '09-14-2016'}}
         ],
         -1  # expected return value for error
        )
    )
    @unpack
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.LOGGER')
    @patch('scripts.consolidate_treatment_arm_collections.consolidate_treatment_arm_collections.MongoDbAccessor')
    def test_main(self, ta_data, tah_data, exp_ret_val, mock_db_accessor, mock_logger):
        mock_db_accessor.get_documents = lambda n: ta_data if n == 'treatmentArm' else tah_data
        mock_db_accessor.get_document_count = lambda n: 0
        ret_val = ctac.main(mock_db_accessor)
        self.assertEqual(ret_val, exp_ret_val)
        mock_logger.info.assert_called()
        if ret_val != 0:
            mock_logger.exception.assert_called_once()


if __name__ == '__main__':
    unittest.main()
