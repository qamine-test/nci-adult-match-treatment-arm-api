#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack

from scripts.summary_report_refresher.refresher import Refresher
from scripts.summary_report_refresher.summary_report import SummaryReport

PAT_STATUS_FLD = 'currentPatientStatus'

DEFAULT_TA = {'_id': '1234567890',
              'treatmentId': 'EAY131-A',
              'version': '2016-08-14',
              'treatmentArmStatus': 'OPEN'}


# Indices for the expected results in test cases below
CURR_IDX = 0
PEND_IDX = 1
FORM_IDX = 2
NOEN_IDX = 3
AREC_IDX = 4

@ddt
class RefresherTest(unittest.TestCase):
    @data(
        ({PAT_STATUS_FLD: 'UNKNOWN_STATUS'}, DEFAULT_TA, [0, 0, 0, 0, []] ),
        ({PAT_STATUS_FLD: 'ON_TREATMENT_ARM'}, DEFAULT_TA, [1, 0, 0, 0, []] ),
        ({PAT_STATUS_FLD: 'PENDING_APPROVAL'}, DEFAULT_TA, [0, 1, 0, 0, []] ),
    )
    @unpack
    def test_match(self, patient, sum_rpt_data, exp_results):
        sr = SummaryReport(sum_rpt_data)
        Refresher._match(patient, sr)
        self.assertEqual(sr.assignmentRecords, exp_results[AREC_IDX])
        self.assertEqual(sr.numNotEnrolledPatient, exp_results[NOEN_IDX])
        self.assertEqual(sr.numPendingArmApproval, exp_results[PEND_IDX])
        self.assertEqual(sr.numFormerPatients, exp_results[FORM_IDX])
        self.assertEqual(sr.numCurrentPatientsOnArm, exp_results[CURR_IDX])


if __name__ == '__main__':
    unittest.main()
