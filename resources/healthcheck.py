import logging

from flask_restful import Resource
from bson.son import SON
from accessors.treatment_arm_accessor import TreatmentArmsAccessor


class HealthCheck(Resource):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.status_pipeline = [
            {"$match": {"dateArchived": None}},
            {"$unwind": "$treatmentArmStatus"},
            {"$group": {"_id": "$treatmentArmStatus", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
        ]

    def get(self):
        self.logger.debug('Retrieving TreatmentArms Healthcheck')
        try:
            accessor = TreatmentArmsAccessor()
            self.logger.debug('connection established.')

            return_info = dict()
            return_info['Total Arm Count'] = accessor.count({})
            return_info['Active Arm Count'] = accessor.count({'dateArchived': None})
            for status in accessor.aggregate(self.status_pipeline):
                return_info['Active Arms in %s Status' % status["_id"]] = status["count"]

            self.logger.debug('Healthcheck returning info: {}'.format(str(return_info)))
            return return_info

        except Exception as ex:
            message = str(ex)
            self.logger.exception(message)
            return message, 500
