from accessors.mongo_db_accessor import MongoDbAccessor
from bson import json_util
import json


class TreatmentArmsAccessor(MongoDbAccessor):
    """
    The TreatmentArm data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'treatmentArms')

    def find(self, query, projection):
        """
        Returns items from the collection using a query and a projection.
        """
        return [json.loads(json_util.dumps(doc)) for doc in self.collection.find(query, projection)]

    def find_one(self, query, projection):
        """
        Returns one element found by filter
        """
        return json.loads(json_util.dumps(
            self.collection.find_one(query, projection)))

    def count(self, query):
        """
        Returns the number of items from the collection using a query.
        """
        return self.collection.count(query)

    def aggregate(self, pipeline):
        """
        Returns the aggregation defined by pipeline.
        """
        return self.collection.aggregate(pipeline)

    def get_ta_non_hotspot_rules(self):
        return [ta_nhr for ta_nhr in self.aggregate([
            {"$match": {"variantReport.nonHotspotRules": {"$ne": []}}},
            {"$unwind": "$variantReport.nonHotspotRules"},
            {"$project": {"treatmentId": 1,
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
        if variant_type not in ['singleNucleotideVariants', 'copyNumberVariants', 'geneFusions', 'indels']:
            raise Exception( "Unknown variant_type '%s' passed to %s" % (variant_type, instance.__class__.__name__))

        return [ta_ir for ta_ir in self.aggregate([
            {"$match": {"variantReport."+variant_type: {"$ne": []}}},
            {"$unwind": "$variantReport."+variant_type},
            {"$project": {"treatmentId": 1,
                          "version": 1,
                          "dateArchived": 1,
                          "treatmentArmStatus": 1,
                          "identifier": "$variantReport."+variant_type+".identifier",
                          "inclusion": "$variantReport."+variant_type+".inclusion",
                          "type": "Hotspot"
                          }}
            ])]
