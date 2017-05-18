"""
The Treatment Arm REST resource
"""

import logging
# import pymongo
# from flask_restful import abort
from flask_restful import reqparse
from flask_restful import Resource
from accessors.treatment_arm_accessor import TreatmentArmsAccessor


# status codes
# 200 - ok
# 400 - bad request (malformed syntax)
# 401 - unauthorized
# 403 - forbidden
# 500 - internal server error (i.e. db not available)

logger = logging.getLogger(__name__)

def is_active_only(active_param):
    # print( f"active_param={active_param}")
    # print( str(active_param and active_param.upper() in ['TRUE', '1']))
    return True if active_param and active_param.upper() in ['TRUE', '1'] else False


def get_args():
    parser = reqparse.RequestParser()
    parser.add_argument('active', help='Return only active arms if set to "true" or "1"')
    parser.add_argument('projection', help='Return only fields of arm specified here.  List should be comma-delimited.')
    args = parser.parse_args()
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
    # import pprint
    # pprint.pprint(args)
    # pprint.pprint(projection)
    return projection


class TreatmentArms(Resource):
    """
    Treatment Arm REST resource
    """
    @staticmethod
    def get():
        """
        Gets the TreatmentArms resource
        """
        args = get_args()
        query = get_query(args)
        projection = get_projection(args)

        # ret_val = None
        # status_code = 200
        # try:
        #     ret_val = TreatmentArmsAccessor().find(query, projection)
        #
        # except pymongo.errors.ServerSelectionTimeoutError as exc:
        #     print( "Caught pymongo.errors.ServerSelectionTimeoutError: ", str(exc))
        #     raise exc
        # except Exception as exc:
        #     status_code = 500
        #     print(str(exc))
        #     abort(500)
        # return ret_val, status_code
        return TreatmentArmsAccessor().find(query, projection)


# class TreatmentArm(Resource):
#     """
#     Treatment Arm REST resource
#     """
#
#     @staticmethod
#     def get(name, version):
#         """
#         Gets the TreatmentArm resource
#         """
#
#         return TreatmentArmsAccessor().find_one(
#             {"name": name, "version": version}, None)
#

class TreatmentArmsById(Resource):
    """
    Treatment Arm REST resource
    """

    @staticmethod
    def get(arm_id):
        """
        Gets the TreatmentArms resource
        """
        args = get_args()
        query = {"treatmentId": arm_id}
        query.update(get_query(args))
        projection = get_projection(args)
        return TreatmentArmsAccessor().find(query, projection)
