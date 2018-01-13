from datetime import datetime

def convert_date(json_date_dict):
    if not isinstance(json_date_dict, dict) or '$date' not in json_date_dict:
        raise TypeError("parameter must be a dict with a '$date' key")
    return datetime.utcfromtimestamp(int(json_date_dict['$date']/1000))


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
            patientType
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
        if 'patientAssignments' in self._pat and 'patientAssignmentLogic' in self._pat['patientAssignments']:
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
        date_assigned = self.get_date_assigned()
        date_on_arm = None
        date_off_arm = None
        last_status = None
        assignment_flag = False

        for trigger in self._pat['patientTriggers']:
            if assignment_flag:
                last_status = trigger['patientStatus']
                if last_status == "ON_TREATMENT_ARM":
                    date_on_arm = convert_date(trigger['dateCreated'])
                elif last_status != "PENDING_APPROVAL":
                    if date_on_arm:
                        date_off_arm = convert_date(trigger['dateCreated'])
                    break
            elif trigger['patientStatus'] == "PENDING_CONFIRMATION":
                # if assignment_flag:
                #     if date_on_arm:
                #         date_off_arm = convert_date(trigger['dateCreated'])
                #     break

                if self._trigger_belongs_to_assignment(trigger, date_assigned):
                    assignment_flag = True
                    last_status = trigger['patientStatus']


        # for trigger in self._pat['patientTriggers']:
        #     if trigger['patientStatus'] == "PENDING_CONFIRMATION":
        #         if assignment_flag:
        #             if date_on_arm:
        #                 date_off_arm = convert_date(trigger['dateCreated'])
        #             break
        #
        #         if self._trigger_belongs_to_assignment(trigger, self._pat['patientAssignments']['dateAssigned']):
        #             assignment_flag = True
        #             last_status = trigger['patientStatus']
        #
        #     elif assignment_flag:
        #         last_status = trigger['patientStatus']
        #         if last_status == "ON_TREATMENT_ARM":
        #             date_on_arm = convert_date(trigger['dateCreated'])
        #         elif last_status != "PENDING_APPROVAL":
        #             if date_on_arm:
        #                 date_off_arm = convert_date(trigger['dateCreated'])
        #             break
        #
        return date_on_arm, date_off_arm, last_status

    @staticmethod
    def _trigger_belongs_to_assignment(trigger, assignment_date):
        """
        Does the given trigger belong to the current assignment for the patient?  It will be considered so if
        if it was created within five minutes of the the assignment_date.
        :param trigger: the trigger being analyzed
        :param assignment_date: a datetime object containing the date the patient as assigned to an arm
        :return: True/False
        """
        belongs = False
        # print("assignment_date ({}), type = {}".format(assignment_date, type(assignment_date)))
        # print("trigger['dateCreated'] ({}), type = {}".format(trigger['dateCreated'], type(trigger['dateCreated'])))

        # delta = convert_date(trigger['dateCreated']) - convert_date(assignment_date)
        delta = convert_date(trigger['dateCreated']) - assignment_date
        # print('Trigger: (' + repr(trigger['dateCreated']) + ') vs (' +
        #       repr(self._pat['patientAssignments']['dateAssigned']) +') delta (' + repr(delta.total_seconds()) + ')')

        # let's give ourselves a 5 min window - is a bit large but ....
        if delta.total_seconds() >= 0 and delta.total_seconds() < 300:
            belongs = True

        return belongs

    # Commented out on 1/13/2018 because not being used.
    # def get_dates_on_off_arm(self):
    #     """
    #     Determines the date the patient went on the arm and the date the patient went off the arm.
    #     If the patient is still on the arm, the date the patient went off the arm will be None.
    #     If the patient never went on the arm, both dates will be None.
    #     :return: a two-item tuple: (date on arm, date off arm)
    #     """
    #     date_on_arm = None
    #     date_off_arm = None
    #     for i, trigger in reversed([(i, trigger) for i, trigger in enumerate(self._pat['patientTriggers'])]):
    #         if trigger['patientStatus'] == "ON_TREATMENT_ARM":
    #             # date_on_arm = trigger['dateCreated']
    #             date_on_arm = convert_date(trigger['dateCreated'])
    #             if i + 1 < len(self._pat['patientTriggers']):
    #                 # date_off_arm = self._pat['patientTriggers'][i+1]['dateCreated']
    #                 date_off_arm = convert_date(self._pat['patientTriggers'][i+1]['dateCreated'])
    #             break
    #
    #     return date_on_arm, date_off_arm
    #
    def get_date_assigned(self):
        """
        Determines the date that the patient was assigned to the arm.
        :return: the date the patient was assigned to the arm; if never assigned to the arm, returns None.
        """
        if 'dateAssigned' in self._pat['patientAssignments']:
            return convert_date(self._pat['patientAssignments']['dateAssigned'])
        else:
            return None

    def get_analysis_id_and_bsn(self):
        """
        Finds the biopsy that matches the Treatment Arm assignment and returns its jobName as the Analysis ID
        along with the corresponding biopsy sequence number.
        :return: a string containing the Analysis ID if one can be found and a string containing the biopsy
                 sequence number; otherwise None, None
        """
        analysis_id = None
        biopsy_seq_num = None
        if 'patientAssignments' in self._pat and 'biopsySequenceNumber' in self._pat['patientAssignments']:
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

        if analysis_id is None and biopsy_seq_num is not None:
            biopsy_seq_num = None

        return analysis_id, biopsy_seq_num

    def get_patient_assignment_step_number(self):
        if 'patientAssignments' in self._pat and 'stepNumber' in self._pat['patientAssignments']:
            return self._pat['patientAssignments']['stepNumber']
        else:
            return None
