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

    def get_dates_on_off_arm(self):

        date_on_arm = None
        date_off_arm = None
        for i, trigger in reversed([(i, trigger) for i, trigger in enumerate(self._pat['patientTriggers'])]):
            if trigger['patientStatus'] == "ON_TREATMENT_ARM":
                date_on_arm = trigger['dateCreated']
                if i + 1 < len(self._pat['patientTriggers']):
                    date_off_arm = self._pat['patientTriggers'][i+1]['dateCreated']
                break

        return (date_on_arm, date_off_arm)

    def get_date_assigned(self):
        if 'dateAssigned' in self._pat['patientAssignments']:
            return self._pat['patientAssignments']['dateAssigned']
        else:
            return None
