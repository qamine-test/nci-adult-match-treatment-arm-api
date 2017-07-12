import unittest
import datetime
import flask
import json
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
    # patient variant report must contain all four
    if len(vr) != 4:
        import pprint
        pprint.pprint(vr)
        raise Exception("bad test data: Patient Variant Report must contain all four required fields.")
    vr['identifier'] = identifier
    vr['confirmed'] = confirmed
    return vr


def add_common_ta_fields(ta_rule, archived, incl, status, trtmt_id, ver, rule_type):
    # Add the fields to ta_rule that are common to both types of treatment arm rules (identifier and NonHotspot).
    ta_rule['treatmentId'] = trtmt_id
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

    # Test the AmoisAnnotator._extract_annot_data function with normal execution.
    @data(
        (ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', False),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}),
        (ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', True),
         {'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True, 'type': 'NonHotspot'}),
        (ta_id_rule('ABCDE', 'EAY131-Q', '2016-11-11', True),
         {'treatmentId': 'EAY131-Q', 'version': '2016-11-11', 'inclusion': True, 'type': 'Hotspot'}),
    )
    @unpack
    def test_extract_annot_data_with_exc(self, amois_dict, exp_annot):
        annot = amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(annot, exp_annot)

    # Test the AmoisAnnotator._extract_annot_data function with exception.
    @data(
        ({'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'},
         "The following required fields were missing from the submitted aMOI: treatmentId"),
        ({'treatmentId': None, 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'},
         "The following required fields were empty in the submitted aMOI: treatmentId"),
    )
    @unpack
    def test_extract_annot_data(self, amois_dict, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.AmoisAnnotator._extract_annot_data(amois_dict)
        self.assertEqual(str(cm.exception), exp_exp_msg)

    # Test the amois.create_amois_annotation function which, in effect, also tests the add() and
    # get() functions of the AmoisAnnotator class.
    @data(
        ([], {}),
        ([ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', False, "OPEN")],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}]}),
        ([ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', True, "OPEN"),
          ta_nh_rule("1", "1", "1", "1", 'EAY131-Q', '2016-12-11', False, "OPEN"),
          ta_id_rule("EDBCA", 'EAY131-P', '2016-11-11', True)],
         {'CURRENT': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': True, 'type': 'Both'},
                      {'treatmentId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False, 'type': 'NonHotspot'}]}),
        ([ta_nh_rule("1", "1", "1", "1", 'EAY131-P', '2016-11-11', False, "OPEN", True),
          ta_nh_rule("1", "1", "1", "1", 'EAY131-Q', '2016-12-11', False, "OPEN"),
          ta_id_rule('COSM6240', 'EAY131-R', '2016-12-12', False, "CLOSED")],
         {'PREVIOUS': [{'treatmentId': 'EAY131-P', 'version': '2016-11-11', 'inclusion': False, 'type': 'NonHotspot'}],
          'CURRENT': [{'treatmentId': 'EAY131-Q', 'version': '2016-12-11', 'inclusion': False, 'type': 'NonHotspot'}],
          'PRIOR': [{'treatmentId': 'EAY131-R', 'version': '2016-12-12', 'inclusion': False, 'type': 'Hotspot'}]}),
    )
    @unpack
    def test_create_amois_annotation(self, amois_list, exp_annotation):
        self.maxDiff = None
        self.assertEqual(amois.create_amois_annotation(amois_list), exp_annotation)


# ******** Test the VariantRulesMgr class in amois.py. ******** #
@ddt
@patch('resources.amois.TreatmentArmsAccessor')
class TestVariantRulesMgr(unittest.TestCase):

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
    def test_match_item(self, vr_item, nhr_item, exp_result, mock_ta_accessor):
        self.assertEqual(amois.VariantRulesMgr._match_item(vr_item, nhr_item), exp_result)

    # Test the VariantRulesMgr._match_var_to_nhr function.
    @data(  # order of params is e, f, g, o
        (variant("4", 'missense', 'IDH1', 'Hotspot'), ta_nh_rule("4", 'missense', 'IDH1', 'Hotspot'), True),
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
    )
    @unpack
    def test_match_var_to_nhr(self, patient_variant, nhr, exp_result, mock_ta_accessor):
        self.assertEqual(amois.VariantRulesMgr._match_var_to_nhr(patient_variant, nhr), exp_result)

    # Test the VariantRulesMgr.get_matching_nonhotspot_rules function.
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
    def test_get_matching_nonhotspot_rules(self, patient_variants, nhr_list, exp_amois_indexes, mock_ta_accessor):
        with APP.test_request_context(''):
            vrm = amois.VariantRulesMgr(nhr_list, {}, {}, {}, {})
            exp_amois = [nhr_list[i] for i in exp_amois_indexes]
            self.assertEqual(vrm.get_matching_nonhotspot_rules(patient_variants), exp_amois)

    # Test the VariantRulesMgr functions that match by identifier:
    #   * get_matching_copy_number_variant_rules
    #   * get_matching_single_nucleotide_variants_rules
    #   * get_matching_gene_fusions_rules
    #   * get_matching_indel_rules
    @data(
        ([], [], []),
        ([variant("9", '1', '1', '1', 'ABCD', True)], [], []),
        ([], [ta_id_rule('ABCDE')], []),
        ([variant("9", '1', '1', '1', 'ABCDE', True)], [ta_id_rule('ABCDE')], [0]),
        ([variant("9", '1', '1', '1', 'ABCDE', False)], [ta_id_rule('ABCDE')], []),
        ([variant("9", '1', '1', '1', 'ABCDE', False), variant("9", '1', '1', '1', 'EDCBA', True)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [1]),
        ([variant("9", '1', '1', '1', 'ABCDE', True), variant("9", '1', '1', '1', 'EDCBA', False)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [0]),
        ([variant("9", '1', '1', '1', 'ABCDE', True), variant("9", '1', '1', '1', 'EDCBA', True)],
         [ta_id_rule('ABCDE'), ta_id_rule('EDCBA')],
         [0, 1]),
    )
    @unpack
    def test_get_matching_identifier_rules(self, patient_variants, ta_id_rules, exp_amois_indexes, mock_ta_accessor):
        with APP.test_request_context(''):
            exp_amois = [ta_id_rules[i] for i in exp_amois_indexes]

            vrm = amois.VariantRulesMgr({}, ta_id_rules, {}, {}, {})
            self.assertEqual(vrm.get_matching_copy_number_variant_rules(patient_variants), exp_amois, "CNV")

            vrm = amois.VariantRulesMgr({}, {}, ta_id_rules, {}, {})
            self.assertEqual(vrm.get_matching_single_nucleotide_variants_rules(patient_variants), exp_amois, "SNV")

            vrm = amois.VariantRulesMgr({}, {}, {}, ta_id_rules, {})
            self.assertEqual(vrm.get_matching_gene_fusions_rules(patient_variants), exp_amois, "GeneFusion")

            vrm = amois.VariantRulesMgr({}, {}, {}, {}, ta_id_rules)
            self.assertEqual(vrm.get_matching_indel_rules(patient_variants), exp_amois, "Indel")


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


# ******** Test the find_amois function in amois.py. ******** #
@ddt
@patch('resources.amois.TreatmentArmsAccessor')
class TestFindAmoisFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with APP.test_request_context(''):
            cls.app = API.app.test_client()

    @data(
        ({
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
          },
         [snv_rules[0], nh_rules[2]]),
        ({
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
         },
         [])
        )
    @unpack
    def test(self, var_rpt, exp_amois_list, mock_ta_accessor):
        self.maxDiff = None
        vrm = amois.VariantRulesMgr(nh_rules, cnv_rules, snv_rules, gf_rules, indel_rules)
        amois_list = amois.find_amois(var_rpt, vrm)
        self.assertEqual(amois_list, exp_amois_list)


# ******** Test the AmoisResource class in amois.py. ******** #
@ddt
@patch('resources.amois.TreatmentArmsAccessor')
@patch('resources.amois.find_amois')
class TestAmoisResource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with APP.test_request_context(''):
            cls.app = API.app.test_client()

    @data(
        ({
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
                    "identifier": "COSM28746",
                    "inclusion": True,
                },
            ],
            "copyNumberVariants": [],
            "indels": [],
            "unifiedGeneFusions": [],
          },
         {'PRIOR': [{'treatmentId': 'SNVARM-A', 'version': '2016-12-20', 'inclusion': True, 'type': 'Hotspot'}],
          'CURRENT': [{'treatmentId': 'NONHOTSPOTARM-B', 'version': '2016-11-20',
                       'inclusion': True, 'type': 'NonHotspot'}],
          },
         [snv_rules[0], nh_rules[2]]),
        ({
             "singleNucleotideVariants": [
                 {  # should NOT match because not confirmed
                     "confirmed": False,
                     "gene": "EFGRB",
                     "oncominevariantclass": "Deleterious",
                     "exon": "14",
                     "function": "frameshiftinsertion",
                     "identifier": "SNVOSN",
                     "inclusion": True,
                 },
             ],
             "unifiedGeneFusions": [],
             "indels": [],
             "copyNumberVariants": [],
         },
         {},
         [])

        )
    @unpack
    def test_patch(self, vr_json, exp_anno_amois, mock_find_amois_ret_val, mock_find_amois, mock_ta_accessor):
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
    def test_patch_with_error(self, vr_json, exp_anno_amois, mock_logging, mock_find_amois, mock_ta_accessor):
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


if __name__ == '__main__':
    unittest.main(verbosity=1)
