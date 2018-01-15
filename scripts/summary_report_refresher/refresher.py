import logging

from accessors.patient_accessor import PatientAccessor
from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from scripts.summary_report_refresher.assignment_record import AssignmentRecord
from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.summary_report import SummaryReport
from resources.auth0_resource import create_authentication_token

PATIENT_STATUS_FIELD = 'currentPatientStatus'
ON_ARM_STATUS = 'ON_TREATMENT_ARM'
PENDING_STATUSES = ['PENDING_APPROVAL', 'PENDING_CONFIRMATION']


class Refresher(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pat_accessor = PatientAccessor()  # provides access to the Patient API
        self.ta_accessor = TreatmentArmsAccessor()  # provides access to the TreatmentArms collection in MongoDB
        self.summary_rpts = [SummaryReport(ta_data)
                             for ta_data in self.ta_accessor.get_arms_for_summary_report_refresh()]
        self.token = create_authentication_token()

    def run(self):
        sum_rpt_cnt = len(self.summary_rpts)
        self.logger.info("{cnt} summary reports selected for update".format(cnt=sum_rpt_cnt))

        upd_cnt = 0
        for sr in self.summary_rpts:
            if self._update_summary_report(sr):
                upd_cnt += 1
            else:
                self.logger.error("Failed to update Summary Report for {trtmtId}:{version}"
                                  .format(trtmtId=sr.treatmentArmId, version=sr.version))

        if upd_cnt != sum_rpt_cnt:
            self.logger.exception("Only {cnt}/{total} summary reports updated".format(cnt=upd_cnt, total=sum_rpt_cnt))
        else:
            self.logger.info("All {cnt} summary reports were updated.".format(cnt=sum_rpt_cnt))

    def _update_summary_report(self, sum_rpt):
        """
        Update the given summary report with counts and assignment records.
        :param sum_rpt: The summary report of a treatment arm that requires updating.
        """
        # Get all patients associated with the Treatment Arm of the given Summary Report.
        # Patients are sorted by patientSequenceNumber (ascending) and patientAssignments.dateConfirmed (descending).
        # patients = [Patient(p) for p in self.pat_accessor.get_patients_by_treatment_arm_id(sum_rpt.treatmentArmId)]
        patients = [Patient(p) for p in self.pat_accessor.get_patients_by_treatment_arm_id(sum_rpt.treatmentArmId,
                                                                                           self.token)]
        self.logger.debug("{cnt} patients returned for '{trtmt_id}"
                          .format(cnt=len(patients), trtmt_id=sum_rpt.treatmentArmId))

        # Update the summary report object for any patients that meet the criteria.
        pat_id = []
        for pat in patients:
            # Only match the patient the first time he/she is encountered.  (A patient can be assigned to an arm more
            # than once [different versions], but only the most recent occurrence should be counted.)
            if pat.patientSequenceNumber not in pat_id:
                Refresher._match(pat, sum_rpt)
                pat_id.append(pat.patientSequenceNumber)

        # Update the summary report in the treatmentArms collection on the database
        return self.ta_accessor.update_summary_report(sum_rpt._id, sum_rpt.get_json())

    @staticmethod
    def _match(patient, sum_rpt):
        assignment_rec = Refresher._create_assignment_record(patient, sum_rpt.treatmentArmId)
        patient_type = Refresher._determine_patient_classification_by_dates(assignment_rec)

        if patient_type is not None:
            sum_rpt.add_patient_by_type(patient_type, assignment_rec)

    @staticmethod
    def _determine_patient_classification_by_dates(assignment_rec):
        """
        Determines if patient is a patient currently on the the Treatment Arm, pending for the Treatment Arm,
        formerly on the Treatment Arm, or once considered but not enrolled on the Treatment Arm.
        :param assignment_rec: an AssignmentRecord for a patient
        :return: SummaryReport.CURRENT, SummaryReport.PENDING, SummaryReport.FORMER, SummaryReport.NOT_ENROLLED, or None
        """
        match_type = None

        if assignment_rec.date_selected:
            if assignment_rec.date_on_arm:
                if assignment_rec.date_off_arm:
                    match_type = SummaryReport.FORMER
                else:
                    match_type = SummaryReport.CURRENT
            elif assignment_rec.assignment_status_outcome in PENDING_STATUSES:
                match_type = SummaryReport.PENDING
            else:
                match_type = SummaryReport.NOT_ENROLLED

        return match_type

    @staticmethod
    def _create_assignment_record(patient, ta_id):
        """
        Creates an assignment record for the given patient based on the given Treatment Arm ID.
        :param patient: the Patient object for the patient
        :param ta_id: the treatment arm ID
        :return: the created AssignmentRecord for patient and ta_id
        """
        ta_version = patient.treatment_arm_version()
        (date_assigned, date_on_arm, date_off_arm, status) = patient.get_dates_status_from_arm()

        analysis_id, biopsy_seq_num = patient.get_analysis_id_and_bsn()
        return AssignmentRecord(patient.patientSequenceNumber,
                                patient.patientType,
                                ta_version,
                                status,
                                patient.get_assignment_reason(ta_id, ta_version),
                                patient.get_patient_assignment_step_number(),
                                patient.diseases,
                                analysis_id,
                                patient.patientAssignmentIdx,
                                biopsy_seq_num,
                                date_assigned,
                                date_on_arm,
                                date_off_arm,
                                )
