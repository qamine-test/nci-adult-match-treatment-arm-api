import logging


class Patient(object):
    """
    An object to store all of the Patient data required for summaryReport refresh.
    The data is formatted in accordance with that of the Patient collection in the match MongoDb database.
    """
    def __init__(self, patient_json):
        self._pat = patient_json



    def __getattr__(self, item):
        return self._pat[item]

    def find_trigger_by_status(self, status):
        """
        Searches the patientTriggers for the matching status
        :param status: the search criterion
        :return: the matching trigger if found, otherwise None
        """
        for trigger in reversed(self._pat['patientTriggers']):
            if trigger['patientStatus'] == status:
                return trigger
        return None

    def treatment_arm_version(self):
        return self._pat['treatmentArm']['version'] if 'treatmentArm' in self._pat else None

    def get_assignment_reason(self, trtmtId, trtmtVersion):
        """
        Find the matching record in the patientAssignmentLogic for the reason the given treatment arm/version
        was assigned.
        :param trtmtId:  the Treatment Arm Identifier
        :param trtmtVersion: the version of the Treatment Arm
        :return: a string describing the reason the assignment was made.
        """
        for assignment_logic in self._pat['patientAssignments']['patientAssignmentLogic']:
            if(assignment_logic['treatmentArmId'] == trtmtId and
               assignment_logic['treatmentArmVersion'] == trtmtVersion):
                return assignment_logic['reason']
        return None
