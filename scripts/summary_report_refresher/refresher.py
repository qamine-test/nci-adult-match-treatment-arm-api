import logging

from accessors.patient_accessor import PatientAccessor
from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from scripts.summary_report_refresher.summary_report import SummaryReport


PATIENT_STATUS_FIELD = 'currentPatientStatus'

class Refresher:
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
        patients = self.pat_accessor.get_patients_by_treatment_arm_id(sum_rpt.treatmentId)
        self.logger.debug("{cnt} patients returned for '{trtmt_id}"
                          .format(cnt=len(patients), trtmt_id=sum_rpt.treatmentId))

        for pat in patients:
            Refresher._match(pat, sum_rpt)

        # TODO not implemented yet
        # self.ta_accessor.update_summary_report(sum_rpt)

    @staticmethod
    def _match(pat, sum_rpt):
        patient_status = pat[PATIENT_STATUS_FIELD]
        if patient_status == 'ON_TREATMENT_ARM':
            sum_rpt.add_patient_by_type(SummaryReport.CURRENT)
        elif patient_status == 'PENDING_APPROVAL':
            sum_rpt.add_patient_by_type(SummaryReport.PENDING)
