import logging

from accessors.treatment_arm_accessor import TreatmentArmsAccessor

class Refresher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.summary_rpts = TreatmentArmsAccessor().find({'dateArchived': None},
                                                         {'treatmentId': 1,
                                                          'version': 1,
                                                          'summaryReport': 1,
                                                          'dateArchived': 1,
                                                          'treatmentArmStatus': 1,
                                                          'stateToken': 1})

    def run(self):
        self.logger.info("{cnt} summary reports selected for update".format(cnt=len(self.summary_rpts)))
