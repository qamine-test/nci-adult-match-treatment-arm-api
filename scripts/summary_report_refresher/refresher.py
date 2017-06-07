import logging

from accessors.patient_accessor import PatientAccessor
from accessors.treatment_arm_accessor import TreatmentArmsAccessor
from summary_report import SummaryReport


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

    # def
