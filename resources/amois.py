"""
The AMOIS REST resource
"""

import logging

from accessors.treatment_arm_accessor import TreatmentArmsAccessor
# from accessors.patient_accessor import PatientAccessor
from flask_restful import Resource, request
from pprint import pformat, pprint

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# LOGGER.addHandler(logging.StreamHandler())


"""
Matching rules for 'exon', 'function', 'oncominevariantclass', 'gene':
   Observations:
   - All four are present in patient variant report (but may be empty)
   - At least one present in nonHotspotRules

   The rules:
   - Matches if not present in nonHotspotRules
   - Matches if empty in patient variant report
   - If present and non-Empty in both, then matches if an exact match

   So, for example:
   If the VR contains 4 in the 'exon', but there is no 'exon' in the nonHotspotRules, the exons match.
   If the VR's 'exon' is empty and there is no 'exon' in the nonHotspotRules, the exons match.
   If the VR's 'exon' is empty and 'exon' in the nonHotspotRules is 3, the exons match.
   If the VR contains 4 in the 'exon', and 'exon' in the nonHotspotRules is 4, the exons match.
   If the VR contains 4 in the 'exon', but 'exon' in the nonHotspotRules is 3, the exons DO NOT match.
   
   Follow the same logic for all four ('exon', 'function', 'oncominevariantclass', 'gene');
   if all four match, it's an aMOI.
"""


def find_amois(vr, var_rules_mgr):
    """
    
    :param vr: patient variantReport dict
    :param var_rules_mgr: instance of the VariantRulesMgr class
    :return: array of items from ta_rules that were a match for the items in the vr
    """
    amois = list()
    amois.extend(var_rules_mgr.get_copy_number_variant_matching_rules(vr['copyNumberVariants']))
    amois.extend(var_rules_mgr.get_gene_fusions_matching_rules(vr['geneFusions']))
    amois.extend(var_rules_mgr.get_single_nucleotide_variants_matching_rules(vr['singleNucleotideVariants']))
    amois.extend(var_rules_mgr.get_indels_matching_rules(vr['indels']))
    amois.extend(var_rules_mgr.get_non_hotspot_matching_rules(vr['singleNucleotideVariants'] + vr['indels']))
    return amois


class VariantRulesMgr:
    def __init__(self, non_hotspot_rules=None,
                 cnv_identifier_rules=None,
                 snv_identifier_rules=None,
                 gene_fusion_identifier_rules=None,
                 indel_identifier_rules=None):
        ta_accessor = TreatmentArmsAccessor()
        self.nhs_rules = non_hotspot_rules if non_hotspot_rules else ta_accessor.get_ta_non_hotspot_rules()
        self.cnv_rules = cnv_identifier_rules if cnv_identifier_rules \
            else ta_accessor.get_ta_identifier_rules('copyNumberVariants')
        self.snv_rules = snv_identifier_rules if snv_identifier_rules \
            else ta_accessor.get_ta_identifier_rules('singleNucleotideVariants')
        self.gf_rules = gene_fusion_identifier_rules if gene_fusion_identifier_rules \
            else ta_accessor.get_ta_identifier_rules('geneFusions')
        self.indel_rules = indel_identifier_rules if indel_identifier_rules \
            else ta_accessor.get_ta_identifier_rules('indels')

    @staticmethod
    def _match_item(variant_item, nhr_item):
        if not nhr_item:
            return True
        if not variant_item:
            return True
        if variant_item == nhr_item:
            return True
        return False

    @staticmethod
    def _match_vr_to_nhr(variant, nhr):
        item_list = ['exon', 'function', 'oncominevariantclass', 'gene']
        pprint(variant)
        pprint(nhr)
        print("\n")
        # ex = nhr['exon']
        print("nhr[exon]")
        for item in item_list:
            if VariantRulesMgr._match_item(variant[item], (nhr[item] if item in nhr else None)):
                return False
        return True

    def get_non_hotspot_matching_rules(self, patient_variants):
        """
        Matches each of the variants to the NonHotspotRules in self.
        :param patient_variants:
        :return: an array containing the rules that matched.
        """
        return [r for r in self.nhs_rules for pv in patient_variants if VariantRulesMgr._match_vr_to_nhr(pv, r)]

    @staticmethod
    def _get_identifier_matching_rules(rule_list, patient_variants):
        """
        Matches each of the variants to each of the rules in rule_list.
        :param rule_list: list of rules with an identifier field
        :param patient_variants: list of variants with an identifier field
        :return: an array containing the rules that matched.
        """
        return [rule for rule in rule_list for var in patient_variants if rule.identifier == var.identifier]

    def get_copy_number_variant_matching_rules(self, patient_variants):
        """
        Matches each of the variants to the CopyNumberVariant rules in self.
        :param patient_variants: list of variants with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_identifier_matching_rules(self.cnv_rules, patient_variants)

    def get_single_nucleotide_variants_matching_rules(self, patient_variants):
        """
        Matches each of the variants to the singleNucleotideVariants rules in self.
        :param patient_variants: list of variants with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_identifier_matching_rules(self.snv_rules, patient_variants)

    def get_gene_fusions_matching_rules(self, patient_variants):
        """
        Matches each of the variants to the geneFusions rules in self.
        :param patient_variants: list of variants with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_identifier_matching_rules(self.cnv_rules, patient_variants)

    def get_indels_matching_rules(self, patient_variants):
        """
        Matches each of the variants to the indel rules in self.
        :param patient_variants: list of variants with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_identifier_matching_rules(self.cnv_rules, patient_variants)


class AmoisAnnotator:
    REQ_FIELDS = ['treatmentId', 'version', 'inclusion']

    def __init__(self):
        self._annotation = dict()

    def add(self, amoi):
        state = AmoisAnnotator._get_amoi_state(amoi)
        annot_data = AmoisAnnotator._extract_annot_data(amoi)
        if state in self._annotation:
            self._annotation[state].append(annot_data)
        else:
            self._annotation[state] = [annot_data]
        # print("annotation after add:\n"+pformat(self._annotation))

    def get(self):
        return self._annotation

    @staticmethod
    def _extract_annot_data(amois):
        return dict([(k, v) for k, v in amois.items() if k in AmoisAnnotator.REQ_FIELDS])

    @staticmethod
    def _get_amoi_state(amoi):
        """
         STATE        treatmentArmStatus        dateArchived
         "CURRENT"    "OPEN"                    None
         "PRIOR"      "SUSPENDED" or "CLOSED"   None
         "FUTURE"     "READY" or "PENDING"      None
         "PREVIOUS"   <doesn't matter>          not None
    
        :param amoi:  Treatment Arm NonHotSpotRules dict
        :return: "PREVIOUS", "FUTURE", "CURRENT", or "PRIOR"
        """
        if amoi['dateArchived']:
            state = "PREVIOUS"
        else:
            ta_status = amoi['treatmentArmStatus']
            if ta_status == "OPEN":
                state = "CURRENT"
            elif ta_status in ["SUSPENDED", "CLOSED"]:
                state = "PRIOR"
            elif ta_status in ["READY", "PENDING"]:
                state = "FUTURE"
            else:
                msg_fmt = "Unknown status '%s' for TreatmentArm '%s', version %s"
                raise Exception(msg_fmt % (ta_status, amoi['treatmentId'], amoi['version']))

        return state


def create_amois_annotation(amois_list):
    """

    :param amois_list:
    :return: dict in the following format: { STATE: [{treatmentId, version, action}, ...], ... }
    """
    annotator = AmoisAnnotator()
    for amoi in amois_list:
        annotator.add(amoi)
    return annotator.get()


class AmoisResource(Resource):

    REQ_VR_FIELDS = ['indels', 'singleNucleotideVariants', 'copyNumberVariants',
                     'nonHotspotRules', 'unifiedGeneFusions', 'geneFusions']

    @staticmethod
    def get_variant_report_arg():
        args = request.get_json()

        LOGGER.debug("ARGS:\n"+pformat(args, width=140, indent=2))
        missing_fields = [f for f in AmoisResource.REQ_VR_FIELDS if f not in args]
        if missing_fields:
            err_msg = ("The following required fields were missing from the variant report: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)
        return args

    @staticmethod
    def get():
        """
        Gets the AMOIS data and annotates the given Variant Report with it.
        
        "amois": { STATE: [{treatmentId, version, action}, ...], ... }
         
        """
        vr = dict()
        status_code = 200
        try:
            vr = AmoisResource.get_variant_report_arg()
            var_rules_mgr = VariantRulesMgr()
            # LOGGER.debug("%d rules loaded from treatmentArms collection" % len(ta_rules))
            amois_list = find_amois(vr, var_rules_mgr)
            vr['amois'] = create_amois_annotation(amois_list)

            LOGGER.debug("VR:\n"+pformat(vr, width=140, indent=2))
        except Exception as exc:
            LOGGER.error(str(exc))
            status_code = 404
        return vr, status_code


if __name__ == '__main__':
    import flask
    import os
    from flask_env import MetaFlaskEnv


    class Configuration(metaclass=MetaFlaskEnv):
        """
        Service configuration
        """
        DEBUG = True
        PORT = 5010
        MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/match')
        # Some instances of the DB are named 'Match' and others 'match'.
        DB_NAME = 'match' if '/match' in MONGODB_URI else 'Match'

    app = flask.Flask(__name__)
    app.config.from_object(Configuration)
    with app.test_request_context(''):
        import pprint
        pprint.pprint(get_ta_non_hotspot_rules())
