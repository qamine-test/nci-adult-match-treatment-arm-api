import unittest
from ddt import ddt, data, unpack
import datetime, sys
sys.path.append("..")
from consolidateTAcollections import cons_ta_colls

@ddt
class TestConsTAColls(unittest.TestCase):

    @data(
        # successful conversion
        ({'_class': 'gov.match.model.TreatmentArm',
          '_id': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         {'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31',
          'dateArchived': None}),
        # 1. exception for missing _id
        ({'_class': 'gov.match.model.TreatmentArm',
          'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 2. exception for passing in already converted record
        ({'_class': 'gov.match.model.TreatmentArm',
          'treatmentId': 'EAY131-Q',
          'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
          'name': 'TDM1 in HER2 Amplification',
          'version': '2016-05-31'},
         'Invalid treatmentArm document'),
        # 3. exception for input record's _id is None
        ({'_class': 'gov.match.model.TreatmentArm',
          '_id': None,
          'dateCreated': datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
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
            ret_doc = cons_ta_colls.TAConverter().convert(ta_doc)
            assert ret_doc == exp_result
        except Exception as e:
            assert str(e) == exp_result

    @data(
        # successful conversion
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
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
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
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
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
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
        # 3. exception for missing dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
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
        # 4. exception for unpopulated dateArchived
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': None,
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
        # 5. exception for missing treatmentArm
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          },
         'Invalid treatmentArmHistory document'
         ),
        # 6. exception for unpopulated treatmentArm[_id]
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'treatmentArm': {'_id': None,
                           'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763093',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK1120212B)',
                                                  'pathway': 'NF1'}],
                           'version': '09-14-2015'}},
         'Invalid treatmentArmHistory document'
         ),
        # 7. exception for missing treatmentArm[_id]
        ({'_class': 'gov.match.model.TreatmentArmHistoryItem',
          '_id': '4300d834-4234-44e3-acdf-65b4a3c444a0',
          'dateArchived': datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
          'treatmentArm': {'dateCreated': datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
                           'name': 'Trametinib in NF1 mutation',
                           'treatmentArmDrugs': [{'drugId': '763093',
                                                  'name': 'Trametinib dimethyl '
                                                          'sulfoxide (GSK1120212B)',
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
            ret_doc = cons_ta_colls.TAHConverter().convert(tah_doc)
            assert ret_doc == exp_result
        except Exception as e:
            assert str(e) == exp_result


    def test_TAConverter_coll_name(self):
        assert cons_ta_colls.TAConverter().get_collection_name() == "treatmentArm"


    def test_TAHConverter_coll_name(self):
        assert cons_ta_colls.TAHConverter().get_collection_name() == "treatmentArmHistory"


if __name__ == '__main__':
    unittest.main()
