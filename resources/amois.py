"""
The AMOIS REST resource

Gets the AMOIS data and annotates the given Variant Report with it in the following format:

"amois": { STATE: [{treatmentArmId, version, inclusion, type}, ...], ... }

    STATE:        will be one of the following:  PRIOR, CURRENT, PREVIOUS, FUTURE
    treatmentArmId:  this is the Treatment Arm ID directly from the treatementArms collection
    version:      this is the version of the Treatment Arm for which the aMOI was found
    inclusion:    boolean - if True, then it's an inclusion aMOI; if False, then it's an exclusion aMOI
    type:         the type of aMOI; will be one of the following:  Hotspot, NonHotspot, Both

An example of how to call this service can be found in scripts/examples/call_amois_svc.py.
"""

import logging
from datetime import datetime, timedelta
from pprint import pformat

from flask_restful import Resource, request

from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from resources.auth0_resource import requires_auth


# NonHotspot Matching rules for 'exon', 'function', 'oncominevariantclass', 'gene':
#    Observations:
#    - For both patient variant and treatment arm variant, any of the four may be blank or absent altogether.
#
#    The rules for matching each of fields:
#      If the field is present and non-empty in the treatment arm variant, then its value must match (case-insensitive)
#      the value of the field in the patient variant.  (So, if the patient variant's field is missing or blank, then
#      the field does not match.)
#
#    So, for example:
#    If the Patient Variant (PV) contains 4 in 'exon', but 'exon' is missing in the Treatment Arm Variant (TAV),
#        the exons match.
#    If the PV's 'exon' is empty and there is no 'exon' in the nonHotspotRules, the exons match.
#    If the PV's 'exon' is empty and 'exon' in the nonHotspotRules is 3, the exons DO NOT match.
#    If the PV contains 4 in the 'exon', and 'exon' in the nonHotspotRules is 4, the exons match.
#    If the PV contains 4 in the 'exon', but 'exon' in the nonHotspotRules is 3, the exons DO NOT match.
#
#    Follow the same logic for all four ('exon', 'function', 'oncominevariantclass', 'gene');
#    if all four match, it's an aMOI.


class VariantRulesMgr:
    def __init__(self, non_hotspot_rules=None,
                 cnv_identifier_rules=None,
                 snv_identifier_rules=None,
                 gene_fusion_identifier_rules=None,
                 indel_identifier_rules=None):
        ta_accessor = TreatmentArmsAccessor()
        self.nhs_rules = non_hotspot_rules if non_hotspot_rules is not None \
            else ta_accessor.get_ta_non_hotspot_rules()
        self.cnv_rules = cnv_identifier_rules if cnv_identifier_rules is not None \
            else ta_accessor.get_ta_identifier_rules('copyNumberVariants')
        self.snv_rules = snv_identifier_rules if snv_identifier_rules is not None \
            else ta_accessor.get_ta_identifier_rules('singleNucleotideVariants')
        self.gf_rules = gene_fusion_identifier_rules if gene_fusion_identifier_rules is not None \
            else ta_accessor.get_ta_identifier_rules('geneFusions')
        self.indel_rules = indel_identifier_rules if indel_identifier_rules is not None \
            else ta_accessor.get_ta_identifier_rules('indels')

    def nonhotspot_rule_count(self):
        return len(self.nhs_rules)

    def copy_number_variant_rule_count(self):
        return len(self.cnv_rules)

    def single_nucleotide_variant_rule_count(self):
        return len(self.snv_rules)

    def gene_fusion_rule_count(self):
        return len(self.gf_rules)

    def indel_rule_count(self):
        return len(self.indel_rules)

    @staticmethod
    def _match_item(variant_item, nhr_item):
        """
        Matches a single item of a patient variant with the corresponding NonHotspotRule (nhr) item.
        :param variant_item: item from patient variant
        :param nhr_item: item from non-hotspot rule (that is, a treatment arm variant)
        :return: True if they match; otherwise False
        """
        if not nhr_item:
            return True  # automatically matches if missing or blank
        if variant_item and str(variant_item).lower() == str(nhr_item).lower():
            return True
        return False

    @staticmethod
    def _match_var_to_nhr(variant, nhr):
        """
        Matches the given variant with the given NonHotspotRule (nhr).
        :param variant: a patient variant
        :param nhr: a non-hotspot rule
        :return: True if they match; otherwise False
        """
        item_list = ['exon', 'function', 'oncominevariantclass', 'gene']
        for item in item_list:
            if not VariantRulesMgr._match_item(variant.get(item, None), nhr.get(item, None)):
                return False
        return True

    @staticmethod
    def _matches_nonhotspot_rule(pv, r):
        return pv['confirmed'] and VariantRulesMgr._match_var_to_nhr(pv, r)

    def get_matching_nonhotspot_rules(self, patient_variant):
        """
        Matches the patient_variant to the NonHotspotRules in self.  NotHotSpotRules are another way of identifying
        if an indel or SNV variant is an aMOI.
        :param patient_variant: an indel or SNV variant from the patient's variant report
        :return: an array containing the rules that matched.
        """
        return [r for r in self.nhs_rules if self._matches_nonhotspot_rule(patient_variant, r)]

    @staticmethod
    def _matches_identifier_rule(pv, r):  # pv=patient variant; r=rule
        return pv['confirmed'] and r['identifier'].lower() == pv['identifier'].lower()

    @classmethod
    def _get_matching_identifier_rules(cls, rule_list, patient_variant):
        """
        Matches the patient_variant to each of the rules in rule_list.
        :param rule_list: list of rules with an identifier field
        :param patient_variant: a variant with an identifier field
        :return: an array containing the rules that matched.
        """
        return [r for r in rule_list if cls._matches_identifier_rule(patient_variant, r)]

    def get_matching_copy_number_variant_rules(self, patient_cnv_variant):
        """
        Matches patient_cnv_variant to the CopyNumberVariant rules in self.
        :param patient_cnv_variant: a CNV variant with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_matching_identifier_rules(self.cnv_rules, patient_cnv_variant)

    def get_matching_single_nucleotide_variant_rules(self, patient_snv_variant):
        """
        Matches patient_snv_variant to the singleNucleotideVariants rules in self.
        :param patient_snv_variant: a SNV variant with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_matching_identifier_rules(self.snv_rules, patient_snv_variant)

    def get_matching_gene_fusions_rules(self, patient_gf_variant):
        """
        Matches patient_gf_variant to the geneFusions rules in self.
        :param patient_gf_variant: a gene fusion variant with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_matching_identifier_rules(self.gf_rules, patient_gf_variant)

    def get_matching_indel_rules(self, patient_indel_variant):
        """
        Matches patient_indel_variant to the indel rules in self.
        :param patient_indel_variant: an indel variant with an identifier field
        :return: an array containing the rules that matched.
        """
        return VariantRulesMgr._get_matching_identifier_rules(self.indel_rules, patient_indel_variant)

    def _is_indel_amoi(self, patient_variant):
        """
        Determines whether or not patient_variant is an indel aMOI.
        :param patient_variant: an indel variant from the patient's variant report
        :return: True/False
        """
        if [r for r in self.indel_rules if self._matches_identifier_rule(patient_variant, r)]:
            return True
        elif [r for r in self.nhs_rules if self._matches_nonhotspot_rule(patient_variant, r)]:
            return True
        else:
            return False

    def _is_single_nucleotide_variant_amoi(self, patient_variant):
        """
        Determines whether or not patient_variant is a SNV aMOI.
        :param patient_variant: a SNV variant from the patient's variant report
        :return: True/False
        """
        if [r for r in self.snv_rules if self._matches_identifier_rule(patient_variant, r)]:
            return True
        elif [r for r in self.nhs_rules if self._matches_nonhotspot_rule(patient_variant, r)]:
            return True
        else:
            return False

    def _is_gene_fusion_amoi(self, patient_variant):
        """
        Determines whether or not patient_variant is a gene fusion aMOI.
        :param patient_variant: an unified gene fusion variant from the patient's variant report
        :return: True/False
        """
        if [r for r in self.gf_rules if self._matches_identifier_rule(patient_variant, r)]:
            return True
        else:
            return False

    def _is_copy_number_variant_amoi(self, patient_variant):
        """
        Determines whether or not patient_variant is a CNV aMOI.
        :param patient_variant: a CNV variant from the patient's variant report
        :return: True/False
        """
        if [r for r in self.cnv_rules if self._matches_identifier_rule(patient_variant, r)]:
            return True
        else:
            return False

    def is_amoi(self, patient_variant, variant_type):
        """
        Determines whether or not patient_variant is an aMOI.
        :param patient_variant: a variant from the patient's variant report
        :param variant_type: patient_variant's type
        :return: True/False
        :raises Exception if variant_type is not one of the valid types
        """
        if variant_type == 'indels':
            return self._is_indel_amoi(patient_variant)
        elif variant_type == 'singleNucleotideVariants':
            return self._is_single_nucleotide_variant_amoi(patient_variant)
        elif variant_type == 'copyNumberVariants':
            return self._is_copy_number_variant_amoi(patient_variant)
        elif variant_type == 'unifiedGeneFusions':
            return self._is_gene_fusion_amoi(patient_variant)
        else:
            raise Exception("Unknown variant type: {}".format(variant_type))


class VariantRulesMgrCache:
    """Caches an instance of the VariantRulesMgr class for a period of time because that class's __init__ always
       reloads the rules from the database.
    """
    _variant_rules_mgr = None
    _interval = 30
    _load_timestamp = datetime.now() - timedelta(seconds=_interval*2)

    @classmethod
    def _reload(cls):
        """
        Creates a new instance of the VariantRulesMgr (which, in effects, reloads the rules from the database)
        and saves the time that it did so.
        """
        cls._variant_rules_mgr = VariantRulesMgr()
        cls._load_timestamp = datetime.now()

        logger = logging.getLogger(__name__)
        logger.debug("{cnt} nonHotspotRules loaded from treatmentArms collection"
                     .format(cnt=cls._variant_rules_mgr.nonhotspot_rule_count()))
        logger.debug("{cnt} SNV Rules loaded from treatmentArms collection"
                     .format(cnt=cls._variant_rules_mgr.single_nucleotide_variant_rule_count()))
        logger.debug("{cnt} CNV Rules loaded from treatmentArms collection"
                     .format(cnt=cls._variant_rules_mgr.copy_number_variant_rule_count()))
        logger.debug("{cnt} Gene Fusions Rules loaded from treatmentArms collection"
                     .format(cnt=cls._variant_rules_mgr.gene_fusion_rule_count()))
        logger.debug("{cnt} Indel Rules loaded from treatmentArms collection"
                     .format(cnt=cls._variant_rules_mgr.indel_rule_count()))

    @classmethod
    def get_variant_rules_mgr(cls):
        """
        If the current instance of VariantRulesMgr is too old, it will be recreated before returning it.
        :return: an up-to-date reference to a VariantRulesMgr object
        """
        seconds_elapsed = (datetime.now() - cls._load_timestamp).seconds
        # logging.getLogger(__name__).debug("seconds_elapsed={}, interval={}".format(seconds_elapsed, cls._interval))
        if seconds_elapsed >= cls._interval:
            cls._reload()
        return cls._variant_rules_mgr


class AmoisAnnotator:
    EQUIV_FIELDS = ['treatmentArmId', 'version', 'inclusion']
    REQ_FIELDS = ['treatmentArmId', 'version', 'inclusion', 'type']

    def __init__(self):
        self._annotation = dict()

    def add(self, amoi):
        state = AmoisAnnotator._get_amoi_state(amoi)
        annot_data = AmoisAnnotator._extract_annot_data(amoi)
        self._add_annot_by_state(state, annot_data)

    def _add_annot_by_state(self, state, annot_data):
        treatment_arm_id = annot_data['treatmentArmId']
        if state in self._annotation:
            state_annots = self._annotation[state]
            if treatment_arm_id in state_annots:
                state_annots[treatment_arm_id].append(annot_data)
            else:
                state_annots[treatment_arm_id] = [annot_data]
        else:
            self._annotation[state] = {treatment_arm_id: [annot_data]}

    def get(self):
        annotations = {}
        for state in self._annotation:
            annot_list = []
            for treatment_arm in self._annotation[state]:
                ta_amoi = {'treatmentArmId': treatment_arm,
                           'inclusions': list(),
                           'exclusions': list()}
                for amoi in self._annotation[state][treatment_arm]:
                    if amoi['inclusion']:
                        ta_amoi['inclusions'].append(amoi['version'])
                    else:
                        ta_amoi['exclusions'].append(amoi['version'])

                    if 'type' not in ta_amoi:
                        ta_amoi['type'] = amoi['type']
                    elif ta_amoi['type'] != amoi['type']:
                        ta_amoi['type'] = "Both"

                ta_amoi['inclusions'] = sorted(set(ta_amoi['inclusions']))
                ta_amoi['exclusions'] = sorted(set(ta_amoi['exclusions']))
                annot_list.append(ta_amoi)
            annotations[state] = annot_list

        return annotations

    @staticmethod
    def _extract_annot_data(amoi):
        missing_fields = [f for f in AmoisAnnotator.REQ_FIELDS if f not in amoi]
        if missing_fields:
            err_msg = ("The following required fields were missing from the submitted aMOI: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)
        error_fields = [f for f in AmoisAnnotator.REQ_FIELDS if amoi[f] is None]
        if error_fields:
            err_msg = ("The following required fields were empty in the submitted aMOI: "
                       + ", ".join(error_fields))
            raise Exception(err_msg)
        return dict([(k, v) for k, v in amoi.items() if k in AmoisAnnotator.REQ_FIELDS])

    @staticmethod
    def _get_amoi_state(amoi):
        """
         STATE        treatmentArmStatus        dateArchived
         "CURRENT"    "OPEN"                    None
         "PRIOR"      "SUSPENDED" or "CLOSED"   None
         "FUTURE"     "READY" or "PENDING"      None
         "PREVIOUS"   <doesn't matter>          not None

        :param amoi:  Treatment Arm Rule dict
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
                raise Exception(msg_fmt % (ta_status, amoi['treatmentArmId'], amoi['version']))

        return state


def find_amois(vr, var_rules_mgr):
    """
    Finds all of the aMOIs for the variants in vr by identifying which ones match the rules in var_rules_mgr.
    Each variant that have one or more aMOIs will have an 'amois' field added to with information about each aMOI.
    :param vr: patient variantReport dict
    :param var_rules_mgr: instance of the VariantRulesMgr class
    """
    for variant in vr['copyNumberVariants']:
        amois = var_rules_mgr.get_matching_copy_number_variant_rules(variant)
        if amois:
            variant['amois'] = create_amois_annotation(amois)

    for variant in vr['unifiedGeneFusions']:
        amois = var_rules_mgr.get_matching_gene_fusions_rules(variant)
        if amois:
            variant['amois'] = create_amois_annotation(amois)

    for variant in vr['indels']:
        amois = var_rules_mgr.get_matching_indel_rules(variant)
        amois.extend(var_rules_mgr.get_matching_nonhotspot_rules(variant))
        if amois:
            variant['amois'] = create_amois_annotation(amois)

    for variant in vr['singleNucleotideVariants']:
        amois = var_rules_mgr.get_matching_single_nucleotide_variant_rules(variant)
        amois.extend(var_rules_mgr.get_matching_nonhotspot_rules(variant))
        if amois:
            variant['amois'] = create_amois_annotation(amois)


def create_amois_annotation(amois_list):
    """
    Given all of the aMOIs in amois_list, assemble all of the required data into format required for annotation.
    :param amois_list:
    :return: dict in the following format: { STATE: [{treatmentArmId, version, action}, ...], ... }
    """
    annotator = AmoisAnnotator()
    for amoi in amois_list:
        annotator.add(amoi)
    return annotator.get()


class AmoisResource(Resource):

    REQ_VR_FIELDS = ['indels', 'singleNucleotideVariants', 'copyNumberVariants', 'unifiedGeneFusions']

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.variant_rules_mgr_cache = VariantRulesMgrCache()

    @staticmethod
    def get_variant_report_arg():
        # print("request is %s" % type(request))
        args = request.get_json()

        # self.logger.debug("ARGS:\n"+pformat(args, width=140, indent=2))
        missing_fields = [f for f in AmoisResource.REQ_VR_FIELDS if f not in args]
        if missing_fields:
            err_msg = ("The following required fields were missing from the variant report: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)
        return args

    @requires_auth
    def patch(self):
        """
        Gets the AMOIS data and annotates the given Variant Report with it in the following format:

        "amois": { STATE: [{treatmentArmId, version, inclusion(True|False), type(Hotspot|NonHotspot|Both)}, ...], ... }

        """
        self.logger.info("Getting annotated aMOI information for Patient Variant Report")
        status_code = 200
        try:
            vr = AmoisResource.get_variant_report_arg()
            self.logger.debug("amois: var_rpt on input:\n" + pformat(vr, width=140, indent=1, depth=2))

            var_rules_mgr = VariantRulesMgrCache.get_variant_rules_mgr()
            # var_rules_mgr = self.variant_rules_mgr_cache.get_variant_rules_mgr()

            find_amois(vr, var_rules_mgr)
            ret_val = vr
        except Exception as exc:
            ret_val = str(exc)
            self.logger.error(ret_val)
            status_code = 404
        return ret_val, status_code


class IsAmoisResource(Resource):
    VARIANT_TYPES = ['indels', 'singleNucleotideVariants', 'copyNumberVariants', 'unifiedGeneFusions']
    REQ_INPUT_FIELDS = ['variants', 'type']

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _get_variants():
        # print("request is %s" % type(request))
        args = request.get_json()

        # self.logger.debug("ARGS:\n"+pformat(args, width=140, indent=2))
        missing_fields = [f for f in IsAmoisResource.REQ_INPUT_FIELDS if f not in args]
        if missing_fields:
            err_msg = ("The following required fields were missing from the input data: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)

        if args['type'] not in IsAmoisResource.VARIANT_TYPES:
            err_msg = "The following is not a valid variant type: '{}'".format(args['type'])
            raise Exception(err_msg)

        return args['type'], args['variants']

    @requires_auth
    def patch(self):
        """
        Given a list of variants of a single, recognized type, returns a list of boolean values that indicates
        if each is an aMOI or not.
        """
        self.logger.info("Getting aMOI information for variants")
        status_code = 200
        try:
            variant_type, variant_list = self._get_variants()
            self.logger.debug("Variant Type = {}".format(variant_type))
            self.logger.debug("Variants =\n{}".format(pformat(variant_list)))
            var_rules_mgr = VariantRulesMgr()
            result_list = [var_rules_mgr.is_amoi(variant, variant_type) for variant in variant_list]
            ret_val = result_list
        except Exception as exc:
            ret_val = str(exc)
            self.logger.error(ret_val)
            status_code = 404
        return ret_val, status_code
