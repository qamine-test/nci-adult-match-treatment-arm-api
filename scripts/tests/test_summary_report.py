#!/usr/bin/env python3

import unittest
from datetime import datetime
from ddt import ddt, data, unpack

from scripts.summary_report_refresher.assignment_record import AssignmentRecord
from scripts.summary_report_refresher.summary_report import SummaryReport

# ******** TEST DATA CONSTANTS ******** #
DEFAULT_SR = {'assignmentRecords': []}
for fld in SummaryReport._SR_COUNT_FIELDS:
    DEFAULT_SR[fld] = 0
DEFAULT_TA = {'_id': '1234567890',
              'treatmentId': 'EAY131-A',
              'version': '2016-08-14',
              'treatmentArmStatus': 'OPEN'}
ALL_FIELDS = SummaryReport._REQ_JSON_FIELDS

# AssignmentRecords data constants
PAT_SEQ_NUM = '112244'
TA_VERSION = '2016-04-25'
ASSNMNT_STATUS = 'ON_TREATMENT_ARM'
ASSNMNT_REASON = 'Because I said so'
STEP_NUM = 1
DISEASES = [
    {
        "_id": "10044409",
        "ctepCategory": "Urothelial Tract Neoplasm",
        "ctepSubCategory": "Urothelial Tract/Bladder Cancer",
        "ctepTerm": "Transitional cell carcinoma of the urothelial tract",
        "shortName": "Transitional cell car. - uroth."
    }
]
ANALYSIS_ID = "AnalysisId"
DATE_SEL = datetime(2016, 4, 1)
DATE_ON_ARM = datetime(2016, 4, 4)
DATE_OFF_ARM = datetime(2016, 5, 1)


# ******** Helper functions to build data structures used in test cases ******** #

def create_assignment_rec():
    return AssignmentRecord(PAT_SEQ_NUM, TA_VERSION, ASSNMNT_STATUS, ASSNMNT_REASON, STEP_NUM,
                            DISEASES, ANALYSIS_ID, DATE_SEL, DATE_ON_ARM, None)


def create_ta_json(omit_flds=None):
    if omit_flds is None:
        return DEFAULT_TA
    else:
        return dict([(f, DEFAULT_TA[f]) for f in DEFAULT_TA if f not in omit_flds])


# ******** Test the SummaryReport class's constructors and get methods in summary_report.py. ******** #
@ddt
class TestSummaryReportConstruction(unittest.TestCase):

    @data(
        (['ALL']),
        (['version', 'treatmentId']),
        (['version']),
    )
    def test_constructor_with_exc(self, missing_field_list):
        if len(missing_field_list) == 1 and missing_field_list[0] == 'ALL':
            sr_json_doc = None
            missing_field_list = ALL_FIELDS
        else:
            sr_json_doc = create_ta_json(missing_field_list)

        with self.assertRaises(Exception) as cm:
            SummaryReport(sr_json_doc)
        exc_str = str(cm.exception)
        self.assertRegex(exc_str,
                         "^The following required fields were missing from the submitted summary report JSON document:")
        for f in missing_field_list:
            self.assertTrue(f in exc_str)

    def test_get_after_normal_construction(self):
        sr = SummaryReport(create_ta_json())
        self.assertEqual(sr._id, DEFAULT_TA['_id'])
        self.assertEqual(sr.treatmentId, DEFAULT_TA['treatmentId'])
        self.assertEqual(sr.version, DEFAULT_TA['version'])
        self.assertEqual(sr.treatmentArmStatus, DEFAULT_TA['treatmentArmStatus'])
        self.assertEqual(sr.assignmentRecords, DEFAULT_SR['assignmentRecords'])
        self.assertEqual(sr.numNotEnrolledPatient, DEFAULT_SR['numNotEnrolledPatient'])
        self.assertEqual(sr.numPendingArmApproval, DEFAULT_SR['numPendingArmApproval'])
        self.assertEqual(sr.numFormerPatients, DEFAULT_SR['numFormerPatients'])
        self.assertEqual(sr.numCurrentPatientsOnArm, DEFAULT_SR['numCurrentPatientsOnArm'])
        self.assertEqual(sr.get_json(), DEFAULT_SR)


# ******** Test the SummaryReport class's other methods in summary_report.py. ******** #
@ddt
class TestSummaryReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_sr = SummaryReport(create_ta_json())

    @data(
        (SummaryReport.NOT_ENROLLED, 1, 0, 0, 0),
        (SummaryReport.NOT_ENROLLED, 2, 0, 0, 0),
        (SummaryReport.CURRENT, 2, 0, 1, 0),
        (SummaryReport.PENDING, 2, 0, 1, 1),
        (SummaryReport.CURRENT, 2, 0, 2, 1),
        (SummaryReport.CURRENT, 2, 0, 3, 1),
        (SummaryReport.FORMER, 2, 1, 3, 1),
    )
    @unpack
    def test_normal_add(self, patient_type, not_enrolled_cnt, former_cnt, current_cnt, pending_cnt):
        self.test_sr.add_patient_by_type(patient_type, create_assignment_rec())
        self.assertEqual(self.test_sr.numNotEnrolledPatient, not_enrolled_cnt)
        self.assertEqual(self.test_sr.numPendingArmApproval, pending_cnt)
        self.assertEqual(self.test_sr.numFormerPatients, former_cnt)
        self.assertEqual(self.test_sr.numCurrentPatientsOnArm, current_cnt)

    def test_add_with_exc(self):
        with self.assertRaises(Exception) as cm:
            self.test_sr.add_patient_by_type('invalidType', create_assignment_rec())
        exc_str = str(cm.exception)
        self.assertEqual(exc_str, "Invalid patient type 'invalidType'")


if __name__ == '__main__':
    unittest.main()
