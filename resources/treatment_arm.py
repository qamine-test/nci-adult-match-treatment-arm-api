"""
The Treatment Arm REST resource
"""

# from flask import jsonify
from flask_restful import reqparse
from flask_restful import Resource
from accessors.treatment_arm_accessor import TreatmentArmsAccessor


# status codes
# 200 - ok
# 400 - bad request (malformed syntax)
# 401 - unauthorized
# 403 - forbidden
# 500 - internal server error (i.e. db not available)

# TO_DO Add projection query parameter where user can specify list of fields to return.  Default to returning all.

def fields_to_projection(field_list):
    """Creates and returns a dict needed to specify projection from field_list."""
    return dict([(f, 1) for f in field_list])


def is_active_only(active_param):
    # print( f"active_param={active_param}")
    # print( str(active_param and active_param.upper() in ['TRUE', '1']))
    return True if active_param and active_param.upper() in ['TRUE', '1'] else False


# SMALL_FIELD_LIST = list(["name", "version", "treatmentId", "dateArchived", "stateToken", "treatmentArmDrugs"])


def get_args():
    parser = reqparse.RequestParser()
    parser.add_argument('active', help='Return only active arms if set to "true" or "1"')
    args = parser.parse_args()
    return args


def get_query(args):
    query = {'dateArchived': {"$eq": None}} if is_active_only(args['active']) else {}
    return query


def get_projection(args):
    projection = None
    if 'projection' in args and args['projection'] is not None:
        projection = {}
        # TO_DO parse projection parameter.
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
     #    import pprint
     # pprint   pprint.pprint(projection)
        return TreatmentArmsAccessor().find(query, projection)
