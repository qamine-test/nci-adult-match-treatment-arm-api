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
        # return self._pat['treatmentArm']['version'] if 'treatmentArm' in self._pat else None
        if 'treatmentArm' in self._pat['patientAssignments']:
            return self._pat['patientAssignments']['treatmentArm']['version']
        else:
            return None


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
        Determines the date the patient was selected for the arm, went on the arm, west off the arm, and the last
        status that is associated with the arm.  (The last status will be one of the following: PENDING_CONFIRMATION,
        PENDING_APPROVAL, ON_TREATMENT_ARM, or the next status after one of these three.)
        - If the patient has been assigned, but not yet put on the arm (in PENDING_* status), then the dates on/off
          the arm will both be None.
        - If the patient is currently on the arm (that is, in ON_TREATMENT_ARM status), the date the patient went off
          the arm will be None.
        - If the patient never went on the arm but was excluded from the study (because of patient refusal, being deemed
          ineligible, or death), then date on arm will be None while the other two dates will have values.
        :return: a four-item tuple: (date assigned to arm, date on arm, date off arm, last status associated with arm)
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
                if self._trigger_belongs_to_assignment(trigger, date_assigned):
                    assignment_flag = True
                    last_status = trigger['patientStatus']

        return date_assigned, date_on_arm, date_off_arm, last_status

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

        delta = convert_date(trigger['dateCreated']) - assignment_date

        # let's give ourselves a 5 min window - is a bit large but ....
        if delta.total_seconds() >= 0 and delta.total_seconds() < 300:
            belongs = True

        return belongs

    def get_date_assigned(self):
        """
        Determines the date that the patient was assigned to the arm.
        :return: the date the patient was assigned to the arm; if never assigned to the arm, returns None.
        """
        if 'dateAssigned' in self._pat['patientAssignments']:
            return convert_date(self._pat['patientAssignments']['dateAssigned'])
        else:  # wouldn't expect this to ever happen
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
        else:  # wouldn't expect this to ever happen
            return None
