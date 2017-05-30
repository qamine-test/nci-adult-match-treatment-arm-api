import unittest
import datetime
# import flask
from ddt import ddt, data, unpack
# from mock import patch
from resources import amois


# def create_vr_dict(e, f, g, o):
#     return { 'exon': e, 'function': f, 'oncominevariantclass': o, 'gene': g}
#
def create_ta_nhr_rule(e, f, g, o, trtmt_id, ver, incl, status='OPEN', archived=False):
    '''Create and return a dictionary containing required fields for a Treatment Arm NonHotspotRule.'''
    ta_vr_rule = create_nhr_dict(e, f, g, o)
    ta_vr_rule['treatmentId'] = trtmt_id
    ta_vr_rule['version'] = ver
    ta_vr_rule['inclusion'] = incl
    ta_vr_rule['dateArchived'] = None if not archived else datetime.datetime(2016, 7, 7)
    ta_vr_rule['treatmentArmStatus'] = status
    return ta_vr_rule

def create_var_rpt(e, f, g, o, identifier='ABC', confirmed=True):
    vr = create_nhr_dict(e, f, g, o)
    # patient variant report must contain all four
    if len(vr) != 4:
        import pprint
        pprint.pprint(vr)
        raise Exception("bad test data: Patient Variant Report must contain all four required fields.")
    vr['identifier'] = identifier
    vr['confirmed'] = confirmed
    return vr

def create_nhr_dict(e, f, g, o):
    ta_vr_rule = dict()
    if e is not None:
        ta_vr_rule['exon'] = e
    if f is not None:
        ta_vr_rule['function'] = f
    if g is not None:
        ta_vr_rule['gene'] = g
    if o is not None:
        ta_vr_rule['oncominevariantclass'] = o
    if not ta_vr_rule:
        raise Exception("bad test data: NonHotspotRule requires at least one field.")
    return ta_vr_rule


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
    def test_get_amoi_state(self, ta_vr_rules, exp_state):
        state = amois.AmoisAnnotator._get_amoi_state(ta_vr_rules)
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
    def test_get_amoi_state_with_exc(self, ta_vr_rules, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.AmoisAnnotator._get_amoi_state(ta_vr_rules)
        self.assertEqual(str(cm.exception), exp_exp_msg)

    # Test the AmoisAnnotator._get_amoi_state function with normal execution.
    @data(
        (create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False}),
        (create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-P', '2016-11-11', True),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True}),
    )
    @unpack
    def test_extract_annot_data(self, amois_dict, exp_annot):
        annot = amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(annot, exp_annot)

    @data(
        ([], {}),
        ([create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN")],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False}]}),
        ([create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN"),
          create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-Q', '2016-12-11', False, "OPEN"), ],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False},
                      {'treatmentId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False}]}),
        ([create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-P', '2016-11-11', False, "OPEN", True),
          create_ta_nhr_rule(1, 1, 1, 1, 'EAY131-Q', '2016-12-11', False, "OPEN"), ],
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
class TestVariantRulesMgr(unittest.TestCase):
    """
    Tests the methods in the VariantRulesMgr class.
    """

    # Test the VariantRulesMgr._match_item function.
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
        self.assertEqual(amois.VariantRulesMgr._match_item(vr_item, nhr_item), exp_result)

    # Test the VariantRulesMgr._match_var_to_nhr function.
    @data( # order of params is e, f, g, o
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', None), True),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', None, 'Hotspot'), True),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, None, 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(None, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, 'missense', 'IDH1', ''), create_nhr_dict(4, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, 'missense', '', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, '', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt('', 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', 'Hotspot'), True),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(14, 'missense', 'IDH1', 'Hotspot'), False),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'),
         create_nhr_dict(4, 'nonframeshiftinsertion', 'IDH1', 'Hotspot'), False),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'ERBB2', 'Hotspot'), False),
        (create_var_rpt(4, 'missense', 'IDH1', 'Hotspot'), create_nhr_dict(4, 'missense', 'IDH1', 'Deleterious'), False),
    )
    @unpack
    def test_match_var_to_nhr(self, variant, nhr, exp_result):
        self.assertEqual(amois.VariantRulesMgr._match_var_to_nhr(variant, nhr), exp_result)

if __name__ == '__main__':
    unittest.main()
