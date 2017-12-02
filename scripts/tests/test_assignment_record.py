#!/usr/bin/env python3

import unittest
from datetime import datetime

from ddt import ddt, data, unpack

from scripts.summary_report_refresher.assignment_record import AssignmentRecord

# ******** TEST DATA CONSTANTS ******** #

PAT_SEQ_NUM = '112233'
TA_VERSION = '2016-04-24'
ASSNMNT_STATUS = 'ON_TREATMENT_ARM'
ASSNMNT_REASON = 'Just because'
STEP_NUM = 1
DISEASES = [
    {
        "_id": "10016180",
        "ctepCategory": "Reproductive System Neoplasm, Female",
        "ctepSubCategory": "Ovarian Cancer (excluding Ovarian Germ Cell Cancer)",
        "ctepTerm": "Fallopian tube carcinoma",
        "shortName": "Fallopian tube carcinoma"
    }
]
ANALYSIS_ID = "TheAnalysisId"
BIOPSY_SEQ_NUM = "BSN12345"
ASSNMNT_IDX = 3
DATE_SEL = datetime(2016, 5, 1)
DATE_ON_ARM = datetime(2016, 5, 4)
DATE_OFF_ARM = datetime(2016, 6, 1)


# ******** Helper functions to build data structures used in test cases ******** #

def create_assignment_rec_args():
    return [PAT_SEQ_NUM, TA_VERSION, ASSNMNT_STATUS, ASSNMNT_REASON, STEP_NUM,
            DISEASES, ANALYSIS_ID, ASSNMNT_IDX, BIOPSY_SEQ_NUM, DATE_SEL, DATE_ON_ARM]


def create_expected_json(date_off_arm):
    return {
        "patientSequenceNumber": PAT_SEQ_NUM,
        "biopsySequenceNumber": BIOPSY_SEQ_NUM,
        "treatmentArmVersion": TA_VERSION,
        "assignmentStatusOutcome": ASSNMNT_STATUS,
        "analysisId": ANALYSIS_ID,
        "dateSelected": DATE_SEL,
        "dateOnArm": DATE_ON_ARM,
        "dateOffArm": date_off_arm,
        "stepNumber": STEP_NUM,
        "diseases": DISEASES,
        "assignmentReason": ASSNMNT_REASON,
        "assignmentReportIdx": ASSNMNT_IDX,
    }


# ******** Test the AssignmentRecord class in assignment_record.py. ******** #
@ddt
class TestAssignmentRecord(unittest.TestCase):
    @data(
        (create_assignment_rec_args(), DATE_OFF_ARM),
        (create_assignment_rec_args(), None),
    )
    @unpack
    def test_get_json(self, constructor_args, date_off_arm):

        constructor_args.append(date_off_arm)
        assignment_rec = AssignmentRecord(*constructor_args)
        exp_json = create_expected_json(date_off_arm)

        self.maxDiff = None
        self.assertEqual(assignment_rec.get_json(), exp_json)


if __name__ == '__main__':
    unittest.main()
