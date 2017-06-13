import logging
from datetime import datetime

from accessors.patient_accessor import PatientAccessor
from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from scripts.summary_report_refresher.assignment_record import AssignmentRecord
from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.summary_report import SummaryReport


PATIENT_STATUS_FIELD = 'currentPatientStatus'
ON_ARM_STATUS = 'ON_TREATMENT_ARM'
PENDING_STATUS = 'PENDING_APPROVAL'

class Refresher:
    OTHER_STATUSES = [
        'OFF_TRIAL_NO_TA_AVAILABLE',
        'OFF_TRIAL_DECEASED',
        'OFF_TRIAL',
        'OFF_TRIAL_BIOPSY_EXPIRED',
        'OFF_TRIAL_NOT_CONSENTED',
        'REJOIN_REQUESTED',
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pat_accessor = PatientAccessor()
        self.ta_accessor = TreatmentArmsAccessor()
        self.summary_rpts = [SummaryReport(ta_data)
                             for ta_data in self.ta_accessor.get_arms_for_summary_report_refresh()]

    def run(self):
        self.logger.info("{cnt} summary reports selected for update".format(cnt=len(self.summary_rpts)))
        for sr in self.summary_rpts:
            self._update_summary_report(sr)

    def _update_summary_report(self, sum_rpt):
        """
        Update the given summary report with counts and assignment records.
        :param sum_rpt: The summary report of a treatment that requires updating.
        """
        # Get all patients associated with the Treatment Arm of the given Summary Report
        patients = [Patient(p) for p in self.pat_accessor.get_patients_by_treatment_arm_id(sum_rpt.treatmentId)]
        self.logger.debug("{cnt} patients returned for '{trtmt_id}"
                          .format(cnt=len(patients), trtmt_id=sum_rpt.treatmentId))

        # Update the summary report object for any patients that meet the criteria.
        for pat in patients:
            Refresher._match(pat, sum_rpt)

        # Update the summary report in the treatmentArms collection on the database
        self.ta_accessor.update_summary_report(sum_rpt._id, sum_rpt.get_json())

    @staticmethod
    def _match(patient, sum_rpt):
        patient_type = Refresher._determine_patient_classification(patient)

        # print("patient_type = {pt}".format(pt=str(patient_type)))

        if patient_type is not None:
            assignment_rec = Refresher._create_assignment_record(patient, sum_rpt.treatmentId)
            sum_rpt.add_patient_by_type(patient_type, assignment_rec)

    @staticmethod
    def _determine_patient_classification(patient):
        """
        Determines if patient is a patient currently on the the Treatment Arm, pending for the Treatment Arm,
        formerly on the Treatment Arm, or once considered but not enrolled on the Treatment Arm.
        :param patient: a Patient
        :return: SummaryReport.CURRENT, SummaryReport.PENDING, SummaryReport.FORMER, SummaryReport.NOT_ENROLLED, or None
        """
        match_type = None

        patient_status = patient.currentPatientStatus
        if patient_status == ON_ARM_STATUS:
            match_type = SummaryReport.CURRENT
        elif patient_status == PENDING_STATUS:
            match_type = SummaryReport.PENDING
        elif patient_status in Refresher.OTHER_STATUSES:
            if patient.find_trigger_by_status(ON_ARM_STATUS) is not None:
                match_type = SummaryReport.FORMER
            elif patient.find_trigger_by_status(PENDING_STATUS) is not None:
                match_type = SummaryReport.NOT_ENROLLED

        return match_type

    # def __init__(self, pat_seq_num, ta_version, assnmnt_status, assnmnt_reason, step_num, diseases, analysis_id,
    #              date_selected, date_on_arm, date_off_arm=None):
    @staticmethod
    def _create_assignment_record(patient, ta_id):
        """

        :param patient:
        :param ta_id:
        :return:
        """
        patient_status = patient.currentPatientStatus
        # trigger = patient.find_trigger_by_status(patient_status)
        ta_version = patient.treatment_arm_version()
        (date_on_arm, date_off_arm) = patient.get_dates_on_off_arm()

        return AssignmentRecord(patient.patientSequenceNumber,
                                ta_version,
                                patient_status,
                                patient.get_assignment_reason(ta_id, ta_version),
                                patient.currentStepNumber,
                                patient.diseases,
                                "todo: analysisId",  # TODO find out where this comes from
                                patient.get_date_assigned(),
                                date_on_arm,
                                date_off_arm
                                )
