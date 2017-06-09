#!/usr/bin/env python3

import unittest
from datetime import datetime

from ddt import ddt, data, unpack
from mock import patch

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
DATE_SEL = datetime(2016, 5, 1)
DATE_ON_ARM = datetime(2016, 5, 4)
DATE_OFF_ARM = datetime(2016, 6, 1)
DATE_NOW = datetime(2016, 7, 1)  # used for mocking datetime.now()


# ******** Helper functions to build data structures used in test cases ******** #

def create_assignment_rec_args():
    return [PAT_SEQ_NUM, TA_VERSION, ASSNMNT_STATUS, ASSNMNT_REASON, STEP_NUM,
            DISEASES, ANALYSIS_ID, DATE_SEL, DATE_ON_ARM]


def create_expected_json(date_off_arm, index):
    if date_off_arm is None:
        time_on_arm = DATE_NOW - DATE_ON_ARM
    else:
        time_on_arm = date_off_arm - DATE_ON_ARM

    return {
        "patientSequenceNumber": PAT_SEQ_NUM,
        "treatmentArmVersion": TA_VERSION,
        "assignmentStatusOutcome": ASSNMNT_STATUS,
        "analysisId": ANALYSIS_ID,
        "dateSelected": DATE_SEL,
        "dateOnArm": DATE_ON_ARM,
        "dateOffArm": date_off_arm,
        "timeOnArm": time_on_arm.total_seconds(),
        "stepNumber": STEP_NUM,
        "diseases": DISEASES,
        "assignmentReason": ASSNMNT_REASON,
        "assignmentReportIdx": index
    }


# ******** Test the AssignmentRecord class in assignment_record.py. ******** #
@ddt
class TestAssignmentRecord(unittest.TestCase):
    @data(
        (create_assignment_rec_args(), DATE_OFF_ARM, 2),
        (create_assignment_rec_args(), None, 3),
    )
    @unpack
    @patch('scripts.summary_report_refresher.assignment_record.datetime')
    def test_get_json(self, contructor_args, date_off_arm, index, mock_datetime):
        # The following mocks ONLY the now() method of datetime; other methods work normally.
        # (See https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking for more info.)
        mock_datetime.now.return_value = DATE_NOW
        mock_datetime.side_effect = datetime

        contructor_args.append(date_off_arm)
        assignment_rec = AssignmentRecord(*contructor_args)
        exp_json = create_expected_json(date_off_arm, index)

        self.maxDiff = None
        self.assertEqual(assignment_rec.get_json(index), exp_json)


if __name__ == '__main__':
    unittest.main()
