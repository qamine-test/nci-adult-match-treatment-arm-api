import logging
from bson.objectid import ObjectId

from accessors.mongo_db_accessor import MongoDbAccessor


class TreatmentArmsAccessor(MongoDbAccessor):
    """
    The TreatmentArm data accessor
    """
    NON_HOTSPOT_RULES_PIPELINE = [
        {"$match": {"variantReport.nonHotspotRules": {"$ne": []}}},
        {"$unwind": "$variantReport.nonHotspotRules"},
        {"$project": {"treatmentArmId": 1,
                      "version": 1,
                      "dateArchived": 1,
                      "treatmentArmStatus": 1,
                      "inclusion": "$variantReport.nonHotspotRules.inclusion",
                      "exon": "$variantReport.nonHotspotRules.exon",
                      "function": "$variantReport.nonHotspotRules.function",
                      "gene": "$variantReport.nonHotspotRules.gene",
                      "oncominevariantclass": "$variantReport.nonHotspotRules.oncominevariantclass",
                      "type": "NonHotspot"
                      }}
    ]

    SUMMARY_REPORT_REFRESH_QUERY = {'dateArchived': None}
    SUMMARY_REPORT_REFRESH_PROJECTION = {'treatmentArmId': 1,
                                        'version': 1,
                                        'treatmentArmStatus': 1,
                                        'stateToken': 1}

    IDENTIFIER_MATCH_STEP = {
        'singleNucleotideVariants': {"variantReport.singleNucleotideVariants": {"$ne": []}},
        'copyNumberVariants': {"variantReport.copyNumberVariants": {"$ne": []}},
        'geneFusions': {"variantReport.geneFusions": {"$ne": []}},
        'indels': {"variantReport.indels": {"$ne": []}},
    }

    IDENTIFIER_UNWIND_STEP = {
        'singleNucleotideVariants': "$variantReport.singleNucleotideVariants",
        'copyNumberVariants': "$variantReport.copyNumberVariants",
        'geneFusions': "$variantReport.geneFusions",
        'indels': "$variantReport.indels",
    }
    IDENTIFIER_PROJECT_STATIC = {"treatmentArmId": 1, "version": 1, "dateArchived": 1,
                                 "treatmentArmStatus": 1, "type": "Hotspot"}
    IDENTIFIER_PROJECT_STEP = {
        'singleNucleotideVariants': dict(**IDENTIFIER_PROJECT_STATIC,
                                         **{'identifier': "$variantReport.singleNucleotideVariants.identifier",
                                            'protein': "$variantReport.singleNucleotideVariants.protein",
                                            'inclusion': "$variantReport.singleNucleotideVariants.inclusion"}),
        'copyNumberVariants': dict(**IDENTIFIER_PROJECT_STATIC,
                                   **{'identifier': "$variantReport.copyNumberVariants.identifier",
                                      'protein': "$variantReport.copyNumberVariants.protein",
                                      'inclusion': "$variantReport.copyNumberVariants.inclusion"}),
        'geneFusions': dict(**IDENTIFIER_PROJECT_STATIC,
                            **{'identifier': "$variantReport.geneFusions.identifier",
                               'protein': "$variantReport.geneFusions.protein",
                               'inclusion': "$variantReport.geneFusions.inclusion"}),
        'indels': dict(**IDENTIFIER_PROJECT_STATIC,
                       **{'identifier': "$variantReport.indels.identifier",
                          'protein': "$variantReport.indels.protein",
                          'inclusion': "$variantReport.indels.inclusion"}),
    }



    def __init__(self):
        MongoDbAccessor.__init__(self, 'treatmentArms', logging.getLogger(__name__))

    def get_ta_non_hotspot_rules(self):
        self.logger.debug('Retrieving TreatmentArms non-Hotspot Rules from database')
        return [ta_nhr for ta_nhr in self.aggregate(self.NON_HOTSPOT_RULES_PIPELINE)]

    def get_ta_identifier_rules(self, variant_type):
        self.logger.debug('Retrieving TreatmentArms Hotspot Rules from database')
        if variant_type not in ['singleNucleotideVariants', 'copyNumberVariants', 'geneFusions', 'indels']:
            raise Exception( "Unknown variant_type '%s' passed to %s" % (variant_type, self.__class__.__name__))

        return [ta_ir for ta_ir in self.aggregate(self._create_identifier_rules_pipeline(variant_type))]

    @classmethod
    def _create_identifier_rules_pipeline(cls, variant_type):
        return [
            {"$match": cls.IDENTIFIER_MATCH_STEP[variant_type]},
            {"$unwind": cls.IDENTIFIER_UNWIND_STEP[variant_type]},
            {"$project": cls.IDENTIFIER_PROJECT_STEP[variant_type]},
        ]

    def get_arms_for_summary_report_refresh(self):
        self.logger.debug('Retrieving TreatmentArms from database for Summary Report Refresh')
        return [ta for ta in self.find(self.SUMMARY_REPORT_REFRESH_QUERY,
                                       self.SUMMARY_REPORT_REFRESH_PROJECTION)]

    def update_summary_report(self, ta_id, sum_rpt_json):
        """
        Updates a single summary report for the document identified by ta_id.
        :param ta_id:  the unique _id for the document in the collection
        :param sum_rpt_json:  the updated summary report
        :returns True/False indicating if it was successful updating the summary report (does NOT imply that it
                 changed any values as it is entirely valid for sum_rpt_json to be exactly the same as what is
                 already in the document)
        """
        ta_id_str = ta_id['$oid']
        self.logger.debug('Updating TreatmentArms with new Summary Report for {_id}'.format(_id=ta_id_str))
        result = self.update_one({'_id': ObjectId(ta_id_str)}, {'$set': {'summaryReport': sum_rpt_json}})
        return result.matched_count == 1  # indicates that it matched an existing document, not that it modified it
