"""
The Treatment Arm REST resource
"""

import logging

from flask_restful import Resource
from flask_restful import request

from accessors.treatment_arm_accessor import TreatmentArmsAccessor


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

    def get(self):
        """
        Gets the TreatmentArms data.
        """
        self.logger.debug("Getting TreatmentArms")
        args = get_args()
        query = get_query(args)
        projection = get_projection(args)

        return TreatmentArmsAccessor().find(query, projection)


class TreatmentArmsById(Resource):
    """
    Treatment Arm REST resource to get Arm by ID
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get(self, arm_id):
        """
        Gets the TreatmentArms data for the arm_id specified.
        """
        self.logger.debug("Getting TreatmentArms by ID: {ARMID}".format(ARMID=arm_id))
        args = get_args()
        query = {"treatmentArmId": arm_id}
        query.update(get_query(args))
        projection = get_projection(args)

        return TreatmentArmsAccessor().find(query, projection)
