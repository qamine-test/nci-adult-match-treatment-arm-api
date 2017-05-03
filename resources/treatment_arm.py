"""
The Treatment Arm REST resource
"""

from flask import jsonify
from flask_restful import Resource
from accessors.treatment_arm_accessor import TreatmentArmAccessor


class TreatmentArms(Resource):
    """
    Treatment Arm REST resource
    """

    def get(self):
        """
        Gets the TreatmentArm resource
        """

        return TreatmentArmAccessor().find({}, {"name": 1, "version": 1})


class TreatmentArm(Resource):
    """
    Treatment Arm REST resource
    """

    def get(self, name, version):
        """
        Gets the TreatmentArm resource
        """

        return TreatmentArmAccessor().find_one(
            {"name": name, "version": version}, None)
