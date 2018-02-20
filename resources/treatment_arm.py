"""
The Treatment Arm REST resource
"""

import logging

from flask_restful import Resource
from flask_restful import request

from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from resources.auth0_resource import requires_auth


def is_active_only(active_param):
    return True if active_param and active_param.upper() in ['TRUE', '1'] else False


def get_args():
    args = request.args.to_dict()
    if 'projection' not in args:
        args['projection'] = None
    if 'active' not in args:
        args['active'] = None
    return args


def get_query(args):
    query = {'dateArchived': {"$eq": None}} if is_active_only(args['active']) else {}
    return query


def get_projection(args):
    projection = None
    if 'projection' in args and args['projection'] is not None:
        projection_list = str.split(args['projection'], ',')
        projection = dict([(f, 1) for f in projection_list])

        # pymongo gives _id even if you don't ask for it, so turn it off if not specifically requested
        if '_id' not in projection:
            projection['_id'] = 0

    return projection


class TreatmentArms(Resource):
    """
    Treatment Arm REST resource
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @requires_auth
    def get(self):
        """
        Gets the TreatmentArms data.
        """
        self.logger.debug("Getting TreatmentArms")
        args = get_args()
        query = get_query(args)
        projection = get_projection(args)

        treatment_arms = TreatmentArmsAccessor().find(query, projection)
        for ta in treatment_arms:
            reformat_status_log(ta)
        return treatment_arms


class TreatmentArmsById(Resource):
    """
    Treatment Arm REST resource to get Arm by ID
    """
    SORT_KEY = 'version'

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @requires_auth
    def get(self, arm_id):
        """
        Gets the TreatmentArms data for the arm_id specified.
        """
        self.logger.debug("Getting TreatmentArms by ID: {ARMID}".format(ARMID=arm_id))
        args = get_args()
        query = {"treatmentArmId": arm_id}
        query.update(get_query(args))
        projection = get_projection(args)

        treatment_arms = TreatmentArmsAccessor().find(query, projection)
        for ta in treatment_arms:
            reformat_status_log(ta)
        return sorted(treatment_arms, key=lambda ta: ta[self.SORT_KEY], reverse=True)


class TreatmentArmsOverview(Resource):
    """
    Treatment Arms REST resource to get overview statistics (counts of arms by status).
    """
    STEPS = [
        {"$unwind": "$treatmentArmStatus"},
        {"$match": {"dateArchived": None}},
        {"$group": {"_id": "$treatmentArmStatus", "count": {"$sum": 1}}},
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @requires_auth
    def get(self):
        """
        Gets the TreatmentArms overview data.
        """
        self.logger.debug("Getting TreatmentArms Overview Data")
        treatment_arms_accessor = TreatmentArmsAccessor()
        counts_by_status = treatment_arms_accessor.aggregate(self.STEPS)

        counts = dict([(cd['_id'], cd['count']) for cd in counts_by_status])
        counts['TOTAL'] = treatment_arms_accessor.count({"dateArchived": None})
        return counts


class TreatmentArmsPTEN(Resource):
    QUERY = {'assayResults.gene': 'PTEN', 'dateArchived': None}
    PROJECTION = {'treatmentArmId': 1, 'version': 1, 'assayResults': 1,
                  'studyTypes': 1, 'dateArchived': 1, "_id": 0}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @requires_auth
    def get(self):
        """
        Gets the TreatmentArms with PTEN Assay.
        """
        self.logger.debug("Getting TreatmentArms with PTEN assay results")
        arms = TreatmentArmsAccessor().find(self.QUERY, self.PROJECTION)
        return [arm for arm in arms if 'OUTSIDE_ASSAY' in arm['studyTypes']]


def reformat_status_log(ta_data):
    """
    The statusLog field in ta_data needs to be reformatted from this:
    "statusLog" : {
        "1488461582089" : "READY",
        "1488461582" : "OPEN"
        "1488461538329" : "PENDING",
    },
    To this:
    "statusLog": [{"date": "1488461538329", "status": "PENDING"},
                  {"date": "1488461582", "status": "OPEN"},
                  {"date": "1488461582089", "status": "READY"}],
    In the new array, it sorted by date in ascending order.
    :param ta_data: treatment arm data that may or may not have a statusLog field
    """
    if 'statusLog' in ta_data:
        status_list = [{"date": status_date, "status": status} for status_date, status in ta_data['statusLog'].items()]
        ta_data['statusLog'] = sorted(status_list, key=lambda item: item['date'])
