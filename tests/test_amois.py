#!/usr/bin/env python3
import datetime
import json
import unittest
from unittest import TestCase

import flask
from ddt import ddt, data, unpack
from flask_env import MetaFlaskEnv
from flask_restful import Api
from mock import patch

from resources import amois

APP = None
API = None


# The following function is called by the Python unittest framework and sets up the Flask application that is
# required in order to test the functionality of the Amois Resource.
def setUpModule():
    class Configuration(metaclass=MetaFlaskEnv):
        """
        Dummied-up service configuration; DB not used in unit-testing but these items are still required.
        """
        DEBUG = True
        PORT = 5010
        MONGODB_URI = 'mongodb://localhost:27017/match'
        # Some instances of the DB are named 'Match' and others 'match'.
        DB_NAME = 'match' if '/match' in MONGODB_URI else 'Match'

    global APP
    APP = flask.Flask(__name__)
    APP.config.from_object(Configuration)
    global API
    API = Api(APP)
    API.add_resource(amois.AmoisResource, '/amois', endpoint='get_amois')
    API.add_resource(amois.IsAmoisResource, '/is_amoi')


# ******** Helper functions to build data structures used in test cases ******** #
def efgo_dict(e, f, g, o):
    # Create and return a dictionary containing 'exon', 'function', 'oncominevariantclass', 'gene'
    efgo_fields = dict()
    if e is not None:
        efgo_fields['exon'] = e
    if f is not None:
        efgo_fields['function'] = f
    if g is not None:
        efgo_fields['gene'] = g
    if o is not None:
        efgo_fields['oncominevariantclass'] = o
    if not efgo_fields:
        raise Exception("bad test data: NonHotspotRule requires at least one field.")
    return efgo_fields


def variant(e, f, g, o, identifier='ABC', confirmed=True):
    # Create a patient variant data structure
    vr = efgo_dict(e, f, g, o)
    # # patient variant report must contain all four
    # if len(vr) != 4:
    #     import pprint
    #     pprint.pprint(vr)
    #     raise Exception("bad test data: Patient Variant Report must contain all four required fields.")
    vr['identifier'] = identifier
    vr['confirmed'] = confirmed
    return vr


def add_common_ta_fields(ta_rule, archived, incl, status, trtmt_id, ver, rule_type):
    # Add the fields to ta_rule that are common to both types of treatment arm rules (identifier and NonHotspot).
    ta_rule['treatmentArmId'] = trtmt_id
    ta_rule['version'] = ver
    ta_rule['inclusion'] = incl
    ta_rule['dateArchived'] = None if not archived else datetime.datetime(2016, 7, 7)
    ta_rule['treatmentArmStatus'] = status
    ta_rule["type"] = rule_type


def ta_nh_rule(e, f, g, o, trtmt_id='TMTID', ver='2016-11-11', incl=True, status='OPEN', archived=False):
    # Create a treatmentArm NonHotspot Rule (matches on the EFGO fields).
    nh_rule = efgo_dict(e, f, g, o)
    add_common_ta_fields(nh_rule, archived, incl, status, trtmt_id, ver, "NonHotspot")
    return nh_rule


def ta_id_rule(identifier, trtmt_id='TMTID', ver='2016-11-11', incl=True, status='OPEN', archived=False):
    # Create a treatmentArm Identifier Rule (matches on identifier field)
    id_rule = {'identifier': identifier}
    add_common_ta_fields(id_rule, archived, incl, status, trtmt_id, ver, "Hotspot")
    return id_rule


# ******** Test the AmoisAnnotator class AND create_amois_annotation function in amois.py. ******** #
@ddt
class TestAmoisAnnotator(unittest.TestCase):

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
        ({'treatmentArmStatus': 'PENDI', 'dateArchived': None, 'treatmentArmId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'PENDI' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': '', 'dateArchived': None, 'treatmentArmId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status '' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': None, 'dateArchived': None, 'treatmentArmId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'None' for TreatmentArm 'EAY-1', version 2016-09-09"),
    )
    @unpack
    def test_get_amoi_state_with_exc(self, ta_vr_rules, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.AmoisAnnotator._get_amoi_state(ta_vr_rules)
        self.assertEqual(str(cm.exception), exp_exp_msg)

    # Test the AmoisAnnotator._extract_annot_data function with normal execution.
    @data(
        (ta_nh_rule("1", "func1", "1", "1", 'EAY131-P', '2016-11-11', False),
         {'treatmentArmId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}),
        (ta_nh_rule("1", "func1", "1", "1", 'EAY131-P', '2016-11-11', True),
         {'treatmentArmId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True, 'type': 'NonHotspot'}),
        (ta_id_rule('ABCDE', 'EAY131-Q', '2016-11-11', True),
         {'treatmentArmId': 'EAY131-Q', 'version': '2016-11-11', 'inclusion': True, 'type': 'Hotspot'}),
    )
    @unpack
    def test_extract_annot_data_with_exc(self, amois_dict, exp_annot):
        annot = amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(annot, exp_annot)

    # Test the AmoisAnnotator._extract_annot_data function with exception.
    @data(
        ({'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'},
         "The following required fields were missing from the submitted aMOI: treatmentArmId"),
        ({'treatmentArmId': None, 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'},
         "The following required fields were empty in the submitted aMOI: treatmentArmId"),
    )
    @unpack
    def test_extract_annot_data(self, amois_dict, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(str(cm.exception), exp_exp_msg)

    # Test the amois.create_amois_annotation function which, in effect, also tests the add() and
    # get() functions of the AmoisAnnotator class.
    @data(
        # 1. No variants in list
        ([], {}),
        # 2. One variant in list
        ([ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', False, "OPEN")],
         {'CURRENT':
            [{'treatmentArmId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}]}),
        # 3. Three variants, two that match the same arm twice (once as hotspot, once as non-hotspot)
        ([ta_nh_rule("1", "func2", "1", "1", 'EAY131-P', '2016-11-11', incl=True, status="OPEN"),
          ta_nh_rule("1", "func3", "1", "1", 'EAY131-Q', '2016-12-11', incl=False, status="OPEN"),
          ta_id_rule("EDBCA", 'EAY131-P', '2016-11-11', incl=True, status="OPEN")],
         {'CURRENT':
            [{'treatmentArmId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True, 'type': 'Both'},
             {'treatmentArmId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False, 'type': 'NonHotspot'}]}),
        # 3. Three variants, each matching different arms with different states
        ([ta_nh_rule("1", "func3", "1", "1", 'EAY131-P', '2016-11-11', False, "OPEN", True),
          ta_nh_rule("1", "func1", "1", "1", 'EAY131-Q', '2016-12-11', False, "OPEN"),
          ta_id_rule('COSM6240', 'EAY131-R', '2016-12-12', False, "CLOSED")],
         {'PREVIOUS':
            [{'treatmentArmId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}],
          'CURRENT':
            [{'treatmentArmId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False, 'type': 'NonHotspot'}],
          'PRIOR':
            [{'treatmentArmId': 'EAY131-R', 'version': '2016-12-12', 'inclusion': False, 'type': 'Hotspot'}]}),
    )
    @unpack
    def test_create_amois_annotation(self, amois_list, exp_annotation):
        self.maxDiff = None
        self.assertEqual(amois.create_amois_annotation(amois_list), exp_annotation)


class AmoisModuleTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        with APP.test_request_context(''):
            cls.app = API.app.test_client()

    def setUp(self):
        ta_accessor_patcher = patch('resources.amois.TreatmentArmsAccessor')
        self.addCleanup(ta_accessor_patcher.stop)
        self.mock_ta_accessor = ta_accessor_patcher.start().return_value


# ******** Test the VariantRulesMgr class in amois.py. ******** #
@ddt
class TestVariantRulesMgr(AmoisModuleTestCase):
    # Test the VariantRulesMgr._match_item function.
    @data(
        ('string_data', 'string_data', True),
        ('string_data', 'STRING_DATa', True),
        ('string_data', 'data_string', False),
        (19, 18, False),
        (19, 19, True),
        (19, '19', True),
        ('', None, True),
        ('19', None, True),
        (19, None, True),
        ('', 19, True),
        ('', '19', True),
        (None, 19, True),
        (None, '19', True),
    )
    @unpack
    def test_match_item(self, vr_item, nhr_item, exp_result):
        self.assertEqual(amois.VariantRulesMgr._match_item(vr_item, nhr_item), exp_result)

    # Test the VariantRulesMgr._match_var_to_nhr function, which matches a patient variant to a nonhotspot rule
    @data(  # order of params is e, f, g, o
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'MISSENSE', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'idh1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', 'hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', None), True),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', None, 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", None, 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule(None, 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', ''), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', '', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", '', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant('', 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("14", 'missense', 'IDH1', 'Hotspot'), False),
        (variant("4", 'missense', 'IDH1', 'Hotspot'),
         ta_nh_rule("4", 'nonframeshiftinsertion', 'IDH1', 'Hotspot'), False),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'ERBB2', 'Hotspot'), False),
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Deleterious'), False),
        (variant("4", None, 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Deleterious'), False),
        (variant("4", None, 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
    )
    @unpack
    def test_match_var_to_nhr(self, patient_variant, nhr, exp_result):
        self.assertEqual(amois.VariantRulesMgr._match_var_to_nhr(patient_variant, nhr), exp_result)

    # Test the VariantRulesMgr.get_matching_nonhotspot_rules_old function.
    @data(
        ([], [], []),
        ([variant("14", 'missense', 'IDH1', 'Hotspot')], [], []),
        ([], ta_nh_rule("12", 'missense', 'ERBB2', 'Hotspot'), []),
        ([variant("14", 'missense', 'IDH2', 'Hotspot')],
         [ta_nh_rule("14", 'missense', None, 'Hotspot')], [0]),
        ([variant("14", 'missense', 'IDH2', 'Hotspot')],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         [1]),
        ([variant("2", 'missense', 'IDH2', 'Hotspot'), variant("14", 'missense', 'IDH2', 'Deleterious')],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         [0]),
        ([variant("14", 'missense', 'IDH2', 'Hotspot'), variant("14", 'missense', 'IDH2', 'Deleterious')],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         [0, 1]),
        ([variant("14", 'missense', 'IDH2', 'Hotspot', 'ABC', False)],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         []),
        ([variant("2", 'missense', 'IDH2', 'Hotspot', 'ABC1', True),
          variant("14", 'missense', 'IDH2', 'Deleterious', 'ABC', False)],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         []),
        ([variant("14", 'missense', 'IDH2', 'Hotspot', 'ABC', False),
          variant("14", 'missense', 'IDH2', 'Deleterious', 'ABC1', False)],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')],
         []),
    )
    @unpack
    def test_get_matching_nonhotspot_rules(self, patient_variants, nhr_list, exp_amois_indexes):
        with APP.test_request_context(''):
            vrm = amois.VariantRulesMgr(nhr_list, {}, {}, {}, {})
            exp_amois = [nhr_list[i] for i in exp_amois_indexes]
            self.assertEqual(vrm.get_matching_nonhotspot_rules_old(patient_variants), exp_amois)

    # Test the VariantRulesMgr functions that match by identifier:
    #   * get_matching_copy_number_variant_rules_old
    #   * get_matching_single_nucleotide_variants_rules_old
    #   * get_matching_gene_fusions_rules_old
    #   * get_matching_indel_rules_old
    @data(
        # 1. No variants, no ID rules
        ([], [], []),
        # 2. One variant, no ID rules
        ([variant("9", '1', '1', '1', 'ABCD', confirmed=True)], [], []),
        # 3. No variants, one ID rule
        ([], [ta_id_rule('ABCDE')], []),
        # 4. One variant (confirmed), one ID rule; matches
        ([variant("9", '1', '1', '1', 'ABCDE', confirmed=True)], [ta_id_rule('ABCDE')], [0]),
        # 5. One variant with lc identifier (confirmed), one ID rule; matches
        ([variant("9", '1', '1', '1', 'abcde', confirmed=True)], [ta_id_rule('ABCDE')], [0]),
        # 6. One variant (unconfirmed), one ID rule; no match
        ([variant("9", '1', '1', '1', 'ABCDE', confirmed=False)], [ta_id_rule('ABCDE')], []),
        # 7. Two variants (unconfirmed & confirmed), two ID rules; match on confirmed variant
        ([variant("9", '1', '1', '1', 'ABCDE', confirmed=False), variant("9", '1', '1', '1', 'EDCBA', True)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [1]),
        # 8. Two variants (confirmed & unconfirmed), two ID rules; match on confirmed variant
        ([variant("9", '1', '1', '1', 'ABCDE', confirmed=True), variant("9", '1', '1', '1', 'EDCBA', False)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [0]),
        # 9. Two variants (both confirmed), two ID rules; match on both variants
        ([variant("9", '1', '1', '1', 'ABCDE', confirmed=True), variant("9", '1', '1', '1', 'EDCBA', True)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [0, 1]),
    )
    @unpack
    def test_get_matching_identifier_rules(self, patient_variants, ta_id_rules, exp_amois_indexes):
        with APP.test_request_context(''):
            exp_amois = [ta_id_rules[i] for i in exp_amois_indexes]

            vrm = amois.VariantRulesMgr({}, ta_id_rules, {}, {}, {})
            self.assertEqual(vrm.get_matching_copy_number_variant_rules_old(patient_variants), exp_amois, "CNV")

            vrm = amois.VariantRulesMgr({}, {}, ta_id_rules, {}, {})
            self.assertEqual(vrm.get_matching_single_nucleotide_variants_rules_old(patient_variants), exp_amois, "SNV")

            vrm = amois.VariantRulesMgr({}, {}, {}, ta_id_rules, {})
            self.assertEqual(vrm.get_matching_gene_fusions_rules_old(patient_variants), exp_amois, "GeneFusion")

            vrm = amois.VariantRulesMgr({}, {}, {}, {}, ta_id_rules)
            self.assertEqual(vrm.get_matching_indel_rules_old(patient_variants), exp_amois, "Indel")

    # Test the VariantRulesMgr._is_indel_amoi function.
    @data(
        (variant("9", '1', '1', '1', 'ABCD', True), [ta_id_rule('ABCDE')], [], False),
        (variant("9", '1', '1', '1', 'ABCDE', True), [ta_id_rule('ABCDE')], [], True),
        (variant("9", '1', '1', '1', 'abcde', True), [ta_id_rule('ABCDE')], [], True),
        (variant("14", 'missense', 'IDH2', 'Hotspot'), [ta_id_rule('ABCDE')],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')], True),
    )
    @unpack
    def test_is_indel_amoi(self, patient_variant, indel_id_rules, nhr_list, exp_result):
        vrm = amois.VariantRulesMgr(nhr_list, {}, {}, {}, indel_id_rules)
        result = vrm._is_indel_amoi(patient_variant)
        self.assertEqual(result, exp_result)

    # Test the VariantRulesMgr._is_single_nucleotide_variant_amoi function.
    @data(
        (variant("8", '1', '1', '1', 'ABCD', True), [ta_id_rule('ABCDE')], [], False),
        (variant("8", '1', '1', '1', 'ABCDE', True), [ta_id_rule('ABCDE')], [], True),
        (variant("8", '1', '1', '1', 'abcde', True), [ta_id_rule('ABCDE')], [], True),
        (variant("14", 'missense', 'IDH2', 'Hotspot'), [ta_id_rule('ABCDE')],
         [ta_nh_rule("14", 'missense', None, 'Deleterious'), ta_nh_rule("14", 'missense', None, 'Hotspot')], True),
    )
    @unpack
    def test_is_single_nucleotide_variant_amoi(self, patient_variant, snv_id_rules, nhr_list, exp_result):
        vrm = amois.VariantRulesMgr(nhr_list, {}, snv_id_rules, {}, {})
        result = vrm._is_single_nucleotide_variant_amoi(patient_variant)
        self.assertEqual(result, exp_result)

    # Test the VariantRulesMgr._is_copy_number_variant_amoi function.
    @data(
        (variant("7", '1', '1', '1', 'ABCD', True), [ta_id_rule('ABCDE')], False),
        (variant("7", '1', '1', '1', 'ABCDE', True), [ta_id_rule('ABCDE')], True),
        (variant("7", '1', '1', '1', 'abcde', True), [ta_id_rule('ABCDE')], True),
    )
    @unpack
    def test_is_copy_number_variant_amoi(self, patient_variant, cnv_id_rules, exp_result):
        vrm = amois.VariantRulesMgr({}, cnv_id_rules, {}, {}, {})
        result = vrm._is_copy_number_variant_amoi(patient_variant)
        self.assertEqual(result, exp_result)

    # Test the VariantRulesMgr._is_gene_fusion_amoi function.
    @data(
        (variant("6", '1', '1', '1', 'ABCD', True), [ta_id_rule('ABCDE')], False),
        (variant("6", '1', '1', '1', 'ABCDE', True), [ta_id_rule('ABCDE')], True),
        (variant("6", '1', '1', '1', 'abcde', True), [ta_id_rule('ABCDE')], True),
    )
    @unpack
    def test_is_gene_fusion_amoi(self, patient_variant, gf_id_rules, exp_result):
        vrm = amois.VariantRulesMgr({}, {}, {}, gf_id_rules, {})
        result = vrm._is_gene_fusion_amoi(patient_variant)
        self.assertEqual(result, exp_result)

    # Test the VariantRulesMgr.is_amoi function with normal execution
    @data(
        (variant("5", '1', '1', '1', 'ABCD', True), [ta_id_rule('ABCDE')], [], False),
        (variant("5", '1', '1', '1', 'ABCDE', True), [ta_id_rule('ABCDE')], [], True),
        (variant("5", '1', '1', '1', 'abcde', True), [ta_id_rule('ABCDE')], [], True),
    )
    @unpack
    def test_is_amoi(self, patient_variant, ta_id_rules, nhr_list, exp_result):
        # Test as CNV
        vrm = amois.VariantRulesMgr(nhr_list, ta_id_rules, {}, {}, {})
        result = vrm.is_amoi(patient_variant, 'copyNumberVariants')
        self.assertEqual(result, exp_result)

        # Test as SNV
        vrm = amois.VariantRulesMgr(nhr_list, {}, ta_id_rules, {}, {})
        result = vrm.is_amoi(patient_variant, 'singleNucleotideVariants')
        self.assertEqual(result, exp_result)

        # Test as unifiedGeneFusions
        vrm = amois.VariantRulesMgr(nhr_list, {}, {}, ta_id_rules, {})
        result = vrm.is_amoi(patient_variant, 'unifiedGeneFusions')
        self.assertEqual(result, exp_result)

        # Test as indels
        vrm = amois.VariantRulesMgr(nhr_list, {}, {}, {}, ta_id_rules)
        result = vrm.is_amoi(patient_variant, 'indels')
        self.assertEqual(result, exp_result)

    # Test the VariantRulesMgr.is_amoi function when invalid variant type causes an exception to be raised.
    def test_is_amoi_with_exc(self):
        invalid_variant_type = 'invalidVariant'
        vrm = amois.VariantRulesMgr({}, {}, {}, {}, {})
        with self.assertRaises(Exception) as cm:
            vrm.is_amoi(variant("9", '1', '1', '1', 'ABCDE', True), invalid_variant_type)
        self.assertEqual(str(cm.exception), "Unknown variant type: {}".format(invalid_variant_type))


# ******** These variables contain source data for the find_amois and AmoisResource tests that follow. ******** #
INCLUSION = True
EXCLUSION = False

nh_rules = list(
    [ta_nh_rule("15", 'func1', 'EGFR', None, 'NONHOTSPOTARM-A', '2016-12-20', INCLUSION, 'SUSPENDED', False),
     ta_nh_rule("15", None, 'EGFR', None, 'NONHOTSPOTARM-A', '2016-12-20', INCLUSION, 'CLOSED', True),
     ta_nh_rule("16", 'func2', 'EGFR', 'OCV1', 'NONHOTSPOTARM-B', '2016-11-20', INCLUSION, 'OPEN', False),
     ta_nh_rule(None, 'func3', 'EGFR', 'OCV1', 'NONHOTSPOTARM-C', '2016-10-20', EXCLUSION, 'OPEN', False),
     ])
cnv_rules = list(
    [ta_id_rule('CNVOSM', 'CNVARM-A', '2016-12-20', INCLUSION, 'SUSPENDED', False),
     ])
snv_rules = list(
    [ta_id_rule('SNVOSM', 'SNVARM-A', '2016-12-20', INCLUSION, 'SUSPENDED', False),
     ])
gf_rules = list(
    [ta_id_rule('GFOSM', 'GENEFUSARM-A', '2016-12-20', INCLUSION, 'SUSPENDED', False),
     ])
indel_rules = list(
    [ta_id_rule('INDOSM', 'INDELARM-A', '2016-12-20', INCLUSION, 'SUSPENDED', False),
     ])

VR_WITH_TWO_SNV_AMOIS = {
    "singleNucleotideVariants": [
        {  # should match on identifier
            "confirmed": True,
            "gene": "EFGR",
            "oncominevariantclass": "Hotspot",
            "exon": "4",
            "function": "missense",
            "identifier": "SNVOSM",
            "inclusion": True,
        },
        {  # should match on NonHotspot Rule
            "confirmed": True,
            "gene": "EGFR",
            "oncominevariantclass": "OCV1",
            "exon": "16",
            "function": "func2",
            "identifier": "COSM28747",
            "inclusion": True,
        },
    ],
    "indels": [],
    "copyNumberVariants": [],
    "unifiedGeneFusions": [],
}

VR_WITH_NO_AMOIS = {
    "singleNucleotideVariants": [
        {  # should NOT match because not confirmed
            "confirmed": False,
            "gene": "EFGR",
            "oncominevariantclass": "Deleterious",
            "exon": "4",
            "function": "func3",
            "identifier": "SNVOSM",
            "inclusion": True,
        },
    ],
    "indels": [],
    "copyNumberVariants": [],
    "unifiedGeneFusions": [],
}


# ******** Test the find_amois function in amois.py. ******** #
@ddt
class TestFindAmoisFunction(AmoisModuleTestCase):

    @data(
        (VR_WITH_TWO_SNV_AMOIS, [snv_rules[0], nh_rules[2]]),
        (VR_WITH_NO_AMOIS, [])
        )
    @unpack
    def test(self, var_rpt, exp_amois_list):
        self.maxDiff = None
        vrm = amois.VariantRulesMgr(nh_rules, cnv_rules, snv_rules, gf_rules, indel_rules)
        amois_list = amois.find_amois(var_rpt, vrm)
        self.assertEqual(amois_list, exp_amois_list)


# ******** Test the AmoisResource class in amois.py. ******** #
@ddt
class TestAmoisResource(AmoisModuleTestCase):

    # Test the AmoisResource.patch function with normal execution
    @data(
        # 1. Test case with two matches
        (VR_WITH_TWO_SNV_AMOIS,
         {'PRIOR': [{'treatmentArmId': 'SNVARM-A', 'version': '2016-12-20', 'inclusion': True, 'type': 'Hotspot'}],
          'CURRENT': [{'treatmentArmId': 'NONHOTSPOTARM-B', 'version': '2016-11-20',
                       'inclusion': True, 'type': 'NonHotspot'}],
          },
         [snv_rules[0], nh_rules[2]]),
        # 2. Test case with no matches
        (VR_WITH_NO_AMOIS, {}, [])
    )
    @unpack
    @patch('resources.amois.find_amois')
    def test_patch(self, vr_json, exp_anno_amois, mock_find_amois_ret_val, mock_find_amois):
        self.maxDiff = None

        mock_find_amois.return_value = mock_find_amois_ret_val
        amois.find_amois = mock_find_amois

        with APP.test_request_context(''):
            exp_result = dict(vr_json)
            if exp_anno_amois:
                exp_result['amois'] = exp_anno_amois

            response = self.app.patch('/amois',
                                      data=json.dumps(vr_json),
                                      content_type='application/json')
            result = json.loads(response.get_data().decode("utf-8"))

            self.assertEqual(result, exp_result)
            self.assertEqual(response.status_code, 200)

    # Test the AmoisResource.patch function with error
    @data(
        ({
            "indels": [],
            "copyNumberVariants": [],
            "unknown1": [],
            "unifiedGeneFusions": [],
          },
         {}),
        ({
             "unknown2": [],
         },
         {})

        )
    @unpack
    @patch('resources.amois.logging')
    def test_patch_with_error(self, vr_json, exp_anno_amois, mock_logging):
        with APP.test_request_context(''):
            exp_result = vr_json
            if exp_anno_amois:
                exp_result['amois'] = exp_anno_amois
            self.maxDiff = None

            response = self.app.patch('/amois',
                                      data=json.dumps(vr_json),
                                      content_type='application/json')
            # self.assertEqual(json.loads(response.get_data().decode("utf-8")), exp_result)
            self.assertEqual(response.status_code, 404)

            mock_logger = mock_logging.getLogger()
            mock_logger.error.assert_called_once()


# ******** Test the IsAmoisResource class in amois.py. ******** #
@ddt
class TestIsAmoisResource(AmoisModuleTestCase):

    # Test the IsAmoisResource._get_variants function
    @data(
        # 1. Valid input of type indels
        ({'type': 'indels',
          'variants': [variant("14", 'missense', 'IDH2', 'Hotspot'), variant("9", '1', '1', '1', 'ABCDE', False)]
          },
         ('indels', [variant("14", 'missense', 'IDH2', 'Hotspot'), variant("9", '1', '1', '1', 'ABCDE', False)])),
        # 2. Valid input of type singleNucleotideVariants
        ({'type': 'singleNucleotideVariants',
          'variants': [variant("14", 'missense', 'IDH2', 'Hotspot')]
          },
         ('singleNucleotideVariants', [variant("14", 'missense', 'IDH2', 'Hotspot')])),
        # 3. Valid input of type copyNumberVariants
        ({'type': 'copyNumberVariants',
          'variants': [variant("9", '1', '1', '1', 'ABCDE', False)]
          },
         ('copyNumberVariants', [variant("9", '1', '1', '1', 'ABCDE', False)])),
        # 4. Valid input of type unifiedGeneFusions
        ({'type': 'unifiedGeneFusions',
          'variants': [variant("9", '1', '1', '1', 'ABCDE', True)]
          },
         ('unifiedGeneFusions', [variant("9", '1', '1', '1', 'ABCDE', True)])),
        # 5. Invalid variant type results in raised exception
        ({'type': 'invalidVariantType',
          'variants': [variant("9", '1', '1', '1', 'ABCDE', True)]
          },
         Exception("The following is not a valid variant type: 'invalidVariantType'")),
        # 6. Missing input field 'variants' results in raised exception
        ({'type': 'unifiedGeneFusions',
          },
         Exception("The following required fields were missing from the input data: variants")),
        # 7. Missing input field 'type' results in raised exception
        ({'variants': [variant("9", '1', '1', '1', 'ABCDE', True)],
          },
         Exception("The following required fields were missing from the input data: type")),
        # 8. Missing input fields 'variants' and 'type' results in raised exception
        ({'variables': [variant("9", '1', '1', '1', 'ABCDE', True)],
          },
         Exception("The following required fields were missing from the input data: variants, type")),
    )
    @unpack
    @patch('resources.amois.request')
    def test_get_variants(self, json_arg, exp_result, mock_request):
        mock_request.get_json.return_value = json_arg

        if isinstance(exp_result, Exception):
            with self.assertRaises(Exception) as cm:
                amois.IsAmoisResource._get_variants()
            self.assertEqual(str(cm.exception), str(exp_result))
        else:
            result = amois.IsAmoisResource._get_variants()
            self.assertEqual(result, exp_result)

    # Test the IsAmoisResource.patch function
    @data(
        ({"type": "unifiedGeneFusions",
          "variants": [variant("9", "1", "1", "1", "ABCDE", True), variant("9", "1", "2", "1", "EDB", False)]
          }, [True, False], [True, False], 200),
        ({"type": "invalidVariantType",
          "variants": [variant("9", "1", "1", "1", "ABCDE", True)]
          }, [True], "The following is not a valid variant type: 'invalidVariantType'", 404)
    )
    @unpack
    @patch('resources.amois.logging')
    @patch('resources.amois.VariantRulesMgr')
    def test_patch(self, json_arg, mock_is_amoi_results, exp_data, exp_status_code, mock_var_rules_mgr, mock_logging):
        mock_var_rules_mgr_inst = mock_var_rules_mgr.return_value
        mock_var_rules_mgr_inst.is_amoi.side_effect = mock_is_amoi_results

        with APP.test_request_context(''):
            response = self.app.patch('/is_amoi',
                                      data=json.dumps(json_arg),
                                      content_type='application/json')
            result_data = json.loads(response.get_data().decode("utf-8"))

            self.assertEqual(result_data, exp_data)
            self.assertEqual(response.status_code, exp_status_code)

            if exp_status_code != 200:
                mock_logger = mock_logging.getLogger()
                mock_logger.error.assert_called_once_with(exp_data)


if __name__ == '__main__':
    unittest.main(verbosity=1)
