"""
Patient MongoDB Accessor
"""

import logging

from accessors.mongo_db_accessor import MongoDbAccessor


class PatientAccessor(MongoDbAccessor):
    """
    The Patient data accessor
    """

    def __init__(self):
        MongoDbAccessor.__init__(self, 'patient', logging.getLogger(__name__))
        # self.logger = logging.getLogger(__name__)

    def get_patients_by_treatment_arm_id(self, trtmt_id):
        """
        Gets patient data for patients associated (currently or formerly) with the given TreatmentId.
        :param trtmt_id: a string containing the TreatmentArm ID
        :return: array of JSON documents containing required fields for Summary Report Refresh analysis
        """
        self.logger.debug('Retrieving Patient documents for Summary Report Refresh analysis')
        return [pat for pat in
                self.aggregate([{"$unwind": "$patientAssignments"},
                                {"$match": {"patientAssignments.treatmentArm._id": trtmt_id}},
                                {"$project": {"currentPatientStatus": 1,
                                              "patientAssignments": 1,
                                              "pattientSequenceNumber": 1,
                                              "currentStepNumber": 1,
                                              "patientTriggers": 1,
                                              "diseases": 1,
                                              "treatmentArm": "$patientAssignments.treatmentArm"}},
                                ])]
