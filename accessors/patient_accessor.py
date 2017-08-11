"""
Patient Accessor
"""

import logging
import json
import requests

from helpers.environment import Environment


# from accessors.mongo_db_accessor import MongoDbAccessor


class PatientAccessor(object):
    """
    The Patient data accessor
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.url = "{}/{}".format(Environment().patient_api_url, 'by_treatment_arm')

    def get_patients_by_treatment_arm_id(self, trtmt_id):
        """
        Gets patient data for patients associated (currently or formerly) with the given TreatmentId.
        The patients will be sorted by patientSequenceNumber (ascending) and patientAssignments.dateConfirmed
        (descending).
        :param trtmt_id: a string containing the TreatmentArm ID
        :return: array of JSON documents containing required fields for Summary Report Refresh analysis
        """
        trtmt_id_url = "{}/{}".format(self.url, trtmt_id)
        self.logger.debug('Retrieving Patient from {}'.format(trtmt_id_url))
        response = requests.get(trtmt_id_url)
        # result = json.loads(response.json().decode("utf-8"))
        result = response.json()

        import pprint
        # pprint.pprint(result, width=200)

        # self.logger.debug("{} Patients returned for arm {}".format(len(result), trtmt_id))
        return result
    # class PatientAccessor(MongoDbAccessor):
    #     """
    #     The Patient data accessor
    #     """
    #     # def __init__(self):
    #     MongoDbAccessor.__init__(self, 'patient', logging.getLogger(__name__))
    #
    # def get_patients_by_treatment_arm_id(self, trtmt_id):
    #     """
    #     Gets patient data for patients associated (currently or formerly) with the given TreatmentId.
    #     The patients will be sorted by patientSequenceNumber (ascending) and patientAssignments.dateConfirmed
    #     (descending).
    #     :param trtmt_id: a string containing the TreatmentArm ID
    #     :return: array of JSON documents containing required fields for Summary Report Refresh analysis
    #     """
    #     self.logger.debug('Retrieving Patient documents for Summary Report Refresh analysis')
    #     return [pat for pat in
    #             self.aggregate([{"$unwind": {"path": "$patientAssignments",
    #                                          "includeArrayIndex": "patientAssignmentIdx"}},
    #                             {"$match": {"patientAssignments.treatmentArm.treatmentArmId": trtmt_id}},
    #                             {"$project": {"currentPatientStatus": 1,
    #                                           "patientAssignmentIdx": 1,
    #                                           "patientAssignments": 1,
    #                                           "patientSequenceNumber": 1,
    #                                           "currentStepNumber": 1,
    #                                           "patientTriggers": 1,
    #                                           "diseases": 1,
    #                                           "biopsies": 1,
    #                                           "treatmentArm": "$patientAssignments.treatmentArm"}},
    #                             {"$sort": {"patientSequenceNumber": 1, "patientAssignments.dateAssigned": -1}},
    #                             ])]
