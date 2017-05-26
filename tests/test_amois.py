import unittest
import datetime
# import flask
from ddt import ddt, data, unpack
# from mock import patch
from resources import amois


# def create_vr_dict(e, f, g, o):
#     return { 'exon': e, 'function': f, 'oncominevariantclass': o, 'gene': g}
#
def create_nhr_dict(e, f, g, o, id, ver, incl, status = 'OPEN', archived = False):
    nhr = dict()
    if e:
        nhr['exon'] = e
    if f:
        nhr['function'] = f
    if g:
        nhr['exon'] = g
    if o:
        nhr['oncominevariantclass'] = o
    if not nhr:
        raise Exception("bad test data: NonHotspotRule requires at least one field.")
    nhr['treatmentId'] = id
    nhr['version'] = ver
    nhr['inclusion'] = incl
    nhr['dateArchived'] = None if not archived else datetime.datetime(2016, 7, 7)
    nhr['treatmentArmStatus'] = status
    return nhr


@ddt
class TestAmoisAnnotator(unittest.TestCase):
    '''Tests the AmoisAnnotator class in amois.py.'''

    # Test the AmoisAnnotator._get_amoi_state function with normal execution.
    @data(
        ({'treatmentArmStatus': 'PENDING', 'dateArchived': None}, 'FUTURE'),
        ({'treatmentArmStatus': 'READY', 'dateArchived': None}, 'FUTURE'),
        ({'treatmentArmStatus': 'OPEN', 'dateArchived': None}, 'CURRENT'),
        ({'treatmentArmStatus': 'CLOSED', 'dateArchived': None}, 'PRIOR'),
        ({'treatmentArmStatus': 'SUSPENDED', 'dateArchived': None}, 'PRIOR'),
        ({'treatmentArmStatus': 'PENDING', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'READY', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'OPEN', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'CLOSED', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'SUSPENDED', 'dateArchived': datetime.datetime.now()}, 'PREVIOUS'),
    )
    @unpack
    def test_get_amoi_state(self, ta_nhr, exp_state):
        state = amois.AmoisAnnotator._get_amoi_state(ta_nhr)
        self.assertEqual(state, exp_state)

    # Test the AmoisAnnotator._get_amoi_state function with exception.
    @data(
        ({'treatmentArmStatus': 'PENDI', 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'PENDI' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': '', 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status '' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': None, 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'None' for TreatmentArm 'EAY-1', version 2016-09-09"),
    )
    @unpack
    def test_get_amoi_state_with_exc(self, ta_nhr, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.AmoisAnnotator._get_amoi_state(ta_nhr)
        self.assertEqual(str(cm.exception), exp_exp_msg)

    # Test the AmoisAnnotator._get_amoi_state function with normal execution.
    @data(
        (create_nhr_dict(1,1,1,1,'EAY131-P', '2016-11-11', False),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False}),
        (create_nhr_dict(1, 1, 1, 1, 'EAY131-P', '2016-11-11', True),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True}),
    )
    @unpack
    def test_extract_annot_data(self, amois_dict, exp_annot):
        annot = amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(annot, exp_annot)

    @data(
        ([], {}),
        ([create_nhr_dict(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN")],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False}]}),
        ([create_nhr_dict(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN"),
          create_nhr_dict(1, 1, 1, 1, 'EAY131-Q', '2016-12-11', False, "OPEN"),],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False},
                      {'treatmentId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False}]}),
        ([create_nhr_dict(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN", True),
          create_nhr_dict(1, 1, 1, 1, 'EAY131-Q', '2016-12-11', False, "OPEN"), ],
         {'PREVIOUS': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False}],
          'CURRENT': [{'treatmentId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False}]}),
    )
    @unpack
    def test_add_and_get(self, amois_list, exp_annotation):
        annotator = amois.AmoisAnnotator()
        for a in amois_list:
            annotator.add(a)
        self.maxDiff = None
        self.assertEqual(annotator.get(), exp_annotation)

@ddt
class TestMatchItem(unittest.TestCase):
    @data(
        ('string_data', 'string_data', True),
        (19, 19, True),
        (19, '19', False),
        ('', None, True),
        ('19', None, True),
        (19, None, True),
        ('', 19, True),
        ('', '19', True),
    )
    @unpack
    def test_match_item(self, vr_item, nhr_item, exp_result):
        self.assertEqual(amois.match_item(vr_item, nhr_item), exp_result)


if __name__ == '__main__':
    unittest.main()
