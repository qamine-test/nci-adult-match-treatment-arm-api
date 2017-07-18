class Patient(object):
    """
    An object to store all of the Patient data required for summaryReport refresh.
    The data is formatted in accordance with that of the Patient collection in the match MongoDb database.
    """
    def __init__(self, patient_json):
        """
        The expected format of the patient_json is that returned by
        accessors.patient_accessor.PatientAccessor.get_patients_by_treatment_arm_id().
        :param patient_json: dictionary containing required patient data
        """
        self._pat = patient_json

    def __getattr__(self, item):
        """
        Provides easy "getter" access to the following items:
            currentPatientStatus
            patientAssignmentIdx
            patientAssignments
            patientSequenceNumber
            currentStepNumber
            patientTriggers
            diseases
            biopsies
            treatmentArm
        :param item: the desired item
        :return: the value of the desired item
        """
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
        """
        Get the treatment arm version for the treatment arm in self.
        :return: a string containing the treatmentArm's version if a treatmentArm is available; otherwise None
        """
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

    def get_dates_status_from_arm(self):
        """
        Determines the date the patient went on/off the arm along with the last status that is associated with the arm.
        If the patient is still on the arm, the date the patient went off the arm will be None.
        If the patient never went on the arm, both dates will be None.
        :return: a three-item tuple: (date on arm, date off arm, last status associated with the arm)
        """
        date_on_arm = None
        date_off_arm = None
        last_status = None
        assignment_flag = False

        for trigger in self._pat['patientTriggers']:
            if trigger['patientStatus'] == "PENDING_CONFIRMATION":
                if assignment_flag:
                    if date_on_arm:
                        date_off_arm = trigger['dateCreated']
                    break

                if self._trigger_belongs_to_assignment(trigger, self._pat['patientAssignments']['dateAssigned']):
                    assignment_flag = True
                    last_status = trigger['patientStatus']

            elif assignment_flag:
                last_status = trigger['patientStatus']
                if last_status == "ON_TREATMENT_ARM":
                    date_on_arm = trigger['dateCreated']
                elif last_status != "PENDING_APPROVAL":
                    if date_on_arm:
                        date_off_arm = trigger['dateCreated']
                    break

        return date_on_arm, date_off_arm, last_status

    @staticmethod
    def _trigger_belongs_to_assignment(trigger, assignment_date):
        """
        Does the given trigger belong to the current assignment for the patient?  It will be considered so if
        if it was created within five minutes of the the assignment_date.
        :param trigger: the trigger being analyzed
        :return: True/False
        """
        belongs = False
        delta = trigger['dateCreated'] - assignment_date
        # print('Trigger: (' + repr(trigger['dateCreated']) + ') vs (' +
        #       repr(self._pat['patientAssignments']['dateAssigned']) +') delta (' + repr(delta.total_seconds()) + ')')

        # let's give ourselves a 5 min window - is a bit large but ....
        if delta.total_seconds() >= 0 and delta.total_seconds() < 300:
            belongs = True

        return belongs

    def get_dates_on_off_arm(self):
        """
        Determines the date the patient went on the arm and the date the patient went off the arm.
        If the patient is still on the arm, the date the patient went off the arm will be None.
        If the patient never went on the arm, both dates will be None.
        :return: a two-item tuple: (date on arm, date off arm)
        """
        date_on_arm = None
        date_off_arm = None
        for i, trigger in reversed([(i, trigger) for i, trigger in enumerate(self._pat['patientTriggers'])]):
            if trigger['patientStatus'] == "ON_TREATMENT_ARM":
                date_on_arm = trigger['dateCreated']
                if i + 1 < len(self._pat['patientTriggers']):
                    date_off_arm = self._pat['patientTriggers'][i+1]['dateCreated']
                break

        return date_on_arm, date_off_arm

    def get_date_assigned(self):
        """
        Determines the date that the patient was assigned to the arm.
        :return: the date the patient was assigned to the arm; if never assigned to the arm, returns None.
        """
        if 'dateAssigned' in self._pat['patientAssignments']:
            return self._pat['patientAssignments']['dateAssigned']
        else:
            return None

    def get_analysis_id(self):
        """
        Finds the biopsy that matches the Treatment Arm assignment and returns its jobName as the Analysis ID.
        :return: a string containing the Analysis ID if one can be found; otherwise None
        """
        analysis_id = None
        biopsy_seq_num = self._pat['patientAssignments']['biopsySequenceNumber']

        for biopsy in self._pat['biopsies']:
            if(not biopsy['failure'] and
               biopsy['biopsySequenceNumber'] == biopsy_seq_num and
               biopsy['nextGenerationSequences'] != []):

                for seq in reversed(biopsy['nextGenerationSequences']):
                    if seq['status'] == 'CONFIRMED':
                        analysis_id = seq['ionReporterResults']['jobName']
                        break
                if analysis_id:
                    break

        return analysis_id

    def get_patient_assignment_step_number(self):
        return self._pat['patientAssignments']['stepNumber']
