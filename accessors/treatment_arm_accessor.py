import logging
from bson.objectid import ObjectId

from accessors.mongo_db_accessor import MongoDbAccessor


class TreatmentArmsAccessor(MongoDbAccessor):
    """
    The TreatmentArm data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'treatmentArms', logging.getLogger(__name__))
        # self.logger = logging.getLogger(__name__)

    def get_ta_non_hotspot_rules(self):
        self.logger.debug('Retrieving TreatmentArms non-Hotspot Rules from database')
        return [ta_nhr for ta_nhr in self.aggregate([
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
            ])]


    def get_ta_identifier_rules(self, variant_type):
        self.logger.debug('Retrieving TreatmentArms Hotspot Rules from database')
        if variant_type not in ['singleNucleotideVariants', 'copyNumberVariants', 'geneFusions', 'indels']:
            raise Exception( "Unknown variant_type '%s' passed to %s" % (variant_type, self.__class__.__name__))

        return [ta_ir for ta_ir in self.aggregate([
            {"$match": {"variantReport."+variant_type: {"$ne": []}}},
            {"$unwind": "$variantReport."+variant_type},
            {"$project": {"treatmentArmId": 1,
                          "version": 1,
                          "dateArchived": 1,
                          "treatmentArmStatus": 1,
                          "identifier": "$variantReport."+variant_type+".identifier",
                          "inclusion": "$variantReport."+variant_type+".inclusion",
                          "type": "Hotspot"
                          }}
            ])]

    def get_arms_for_summary_report_refresh(self):
        self.logger.debug('Retrieving TreatmentArms from database for Summary Report Refresh')
        return [ta for ta in self.find({'dateArchived': None},
                                       {'treatmentArmId': 1,
                                        'version': 1,
                                        'treatmentArmStatus': 1,
                                        'stateToken': 1})]

    def update_summary_report(self, ta_id, sum_rpt_json):
        """
        Updates a single summary report for the document identified by ta_id.
        :param ta_id:  the unique _id for the document in the collection
        :param sum_rpt_json:  the updated summary report
        :returns True/False indicating if it was successful updating the summary report
        """
        ta_id_str = ta_id['$oid']
        self.logger.debug('Updating TreatmentArms with new Summary Report for {_id}'.format(_id=ta_id_str))
        result = self.update_one({'_id': ObjectId(ta_id_str)}, {'$set': {'summaryReport': sum_rpt_json}})
        return result.modified_count == 1
