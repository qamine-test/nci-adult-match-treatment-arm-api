class AssignmentRecord(object):
    """
    An object to store all of the data required in the AssignmentRecords field of the summaryReport
    subcollection of the TreatmentArms collection in the match MongoDb database.
    """

    def __init__(self, pat_seq_num, patient_type, ta_version, assnmnt_status, assnmnt_reason, step_num, diseases,
                 analysis_id, patient_assmt_idx, biopsy_seq_num, date_selected, date_on_arm, date_off_arm=None):

        self.patient_sequence_number = pat_seq_num
        self.patient_type = patient_type
        self.treatment_arm_version = ta_version
        self.assignment_status_outcome = assnmnt_status
        self.analysis_id = analysis_id
        self.patient_assmt_idx = patient_assmt_idx
        self.date_selected = date_selected
        self.date_on_arm = date_on_arm
        self.date_off_arm = date_off_arm
        self.step_number = step_num
        self.diseases = diseases
        self.assignment_reason = assnmnt_reason
        self.biopsy_seq_num = biopsy_seq_num

    def get_json(self):
        """
        Creates the required format for an AssignmentRecord in the summary report.
        :return: the dict containing all of the data
        """
        return {
            "patientSequenceNumber": self.patient_sequence_number,
            "patientType": self.patient_type,
            "treatmentArmVersion": self.treatment_arm_version,
            "assignmentStatusOutcome": self.assignment_status_outcome,
            "analysisId": self.analysis_id,
            "biopsySequenceNumber": self.biopsy_seq_num,
            "dateSelected": self.date_selected,
            "dateOnArm": self.date_on_arm,
            "dateOffArm": self.date_off_arm,
            "stepNumber": self.step_number,
            "diseases": self.diseases,
            "assignmentReason": self.assignment_reason,
            "assignmentReportIdx": self.patient_assmt_idx
        }
