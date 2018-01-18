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
              'treatmentArmId': 'EAY131-A',
              'version': '2016-08-14',
              'treatmentArmStatus': 'OPEN'}
ALL_FIELDS = SummaryReport._REQ_JSON_FIELDS

# AssignmentRecords data constants
PAT_SEQ_NUM = '112244'
PATIENT_TYPE = 'STANDARD'
TA_VERSION = '2016-04-25'
BIOPSY_SEQ_NUM = 'BSN-112244'
ASSNMNT_STATUS = 'ON_TREATMENT_ARM'
ASSNMNT_REASON = 'Because I said so'
STEP_NUM = 0
DISEASES = [
    {
        "_id": "10044409",
        "ctepCategory": "Urothelial Tract Neoplasm",
        "ctepSubCategory": "Urothelial Tract/Bladder Cancer",
        "ctepTerm": "Transitional cell carcinoma of the urothelial tract",
        "shortName": "Transitional cell car. - uroth."
    }
]
ASSNMNT_IDX = 2
ANALYSIS_ID = "AnalysisId"
DATE_SEL = datetime(2016, 4, 1)
DATE_ON_ARM = datetime(2016, 4, 4)
DATE_OFF_ARM = datetime(2016, 5, 1)


# ******** Helper functions to build data structures used in test cases ******** #

def create_assignment_rec(date_selected=None, date_on_arm=None, date_off_arm=None, assignment_status=ASSNMNT_STATUS):
    return AssignmentRecord(PAT_SEQ_NUM, PATIENT_TYPE, TA_VERSION, assignment_status, ASSNMNT_REASON, STEP_NUM,
                            DISEASES, ASSNMNT_IDX, ANALYSIS_ID, BIOPSY_SEQ_NUM,
                            date_selected, date_on_arm, date_off_arm)

PENDING_ASSMT_REC = create_assignment_rec(date_selected=DATE_SEL, date_on_arm=None, date_off_arm=None,
                                          assignment_status="PENDING_CONFIRMATION")
NOT_ENROLLED_ASSMT_REC = create_assignment_rec(date_selected=DATE_SEL, date_on_arm=None, date_off_arm=DATE_OFF_ARM,
                                               assignment_status="COMPASSIONATE_CARE")
CURRENTLY_ON_TA_ASSMT_REC = create_assignment_rec(date_selected=DATE_SEL, date_on_arm=DATE_ON_ARM, date_off_arm=None,
                                                  assignment_status="ON_TREATMENT_ARM")
FORMERLY_ON_TA_AR = create_assignment_rec(date_selected=DATE_SEL, date_on_arm=DATE_ON_ARM, date_off_arm=DATE_OFF_ARM,
                                          assignment_status="FORMERLY_ON_ARM_OFF_TRIAL")


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
        (['version', 'treatmentArmId']),
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
        self.assertEqual(sr.treatmentArmId, DEFAULT_TA['treatmentArmId'])
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
        (SummaryReport.NOT_ENROLLED, NOT_ENROLLED_ASSMT_REC, 1, 0, 0, 0),
        (SummaryReport.NOT_ENROLLED, NOT_ENROLLED_ASSMT_REC, 2, 0, 0, 0),
        (SummaryReport.CURRENT, CURRENTLY_ON_TA_ASSMT_REC, 2, 0, 1, 0),
        (SummaryReport.PENDING, PENDING_ASSMT_REC, 2, 0, 1, 1),
        (SummaryReport.CURRENT, CURRENTLY_ON_TA_ASSMT_REC, 2, 0, 2, 1),
        (SummaryReport.CURRENT, CURRENTLY_ON_TA_ASSMT_REC, 2, 0, 3, 1),
        (SummaryReport.FORMER, FORMERLY_ON_TA_AR, 2, 1, 3, 1),
    )
    @unpack
    def test_counters_after_normal_add(self, patient_type, assmt_rec, not_enrolled_cnt,
                                       former_cnt, current_cnt, pending_cnt):
        """
        This test just verifies the expected value of the counter fields of the SummaryReport object.
        The assignmentRecords field is confirmed elsewhere.
        """
        self.test_sr.add_patient_by_type(patient_type, assmt_rec)
        self.assertEqual(self.test_sr.numNotEnrolledPatient, not_enrolled_cnt)
        self.assertEqual(self.test_sr.numPendingArmApproval, pending_cnt)
        self.assertEqual(self.test_sr.numFormerPatients, former_cnt)
        self.assertEqual(self.test_sr.numCurrentPatientsOnArm, current_cnt)

    def test_add_with_exc(self):
        with self.assertRaises(Exception) as cm:
            self.test_sr.add_patient_by_type('invalidType', create_assignment_rec())
        exc_str = str(cm.exception)
        self.assertEqual(exc_str, "Invalid patient type 'invalidType'")

    @data(
        # 1.  Not selected for arm (shouldn't ever happen in real world scenario because of how patients are
        #     pulled from the database)
        (create_assignment_rec(date_selected=None, date_on_arm=None, date_off_arm=None), False),
        # 2.  Patient in PENDING_CONFIRMATION or PENDING_APPROVAL
        (PENDING_ASSMT_REC, True),
        # 3.  Patient not enrolled (selected but never put on arm)
        (NOT_ENROLLED_ASSMT_REC, False),
        # 4.  Patient currently on treatment arm
        (CURRENTLY_ON_TA_ASSMT_REC, True),
        # 5.  Patient formerly on treatment arm
        (FORMERLY_ON_TA_AR, True),
    )
    @unpack
    def test_assignment_occupies_slot(self, assignment_record, exp_result):
        result = SummaryReport._assignment_occupies_slot(assignment_record.get_json())
        self.assertEqual(result, exp_result)


    @data(
        # 1. Test get_json immediately after construction
        ([], DEFAULT_SR),
        # 2. Test get_json after three patients added
        ([(SummaryReport.NOT_ENROLLED, NOT_ENROLLED_ASSMT_REC),
          (SummaryReport.CURRENT, CURRENTLY_ON_TA_ASSMT_REC),
          (SummaryReport.PENDING, PENDING_ASSMT_REC),
          ],
         {'assignmentRecords': [NOT_ENROLLED_ASSMT_REC.get_json(),
                                dict(**CURRENTLY_ON_TA_ASSMT_REC.get_json(), **{"slot": 1}),
                                dict(**PENDING_ASSMT_REC.get_json(), **{"slot": 2})],
          'numNotEnrolledPatient': 1, 'numFormerPatients': 0, 'numCurrentPatientsOnArm': 1, 'numPendingArmApproval': 1})
    )
    @unpack
    def test_get_json(self, test_patients, exp_result):
        sr = SummaryReport(create_ta_json())
        for patient_type, assignment_record in test_patients:
            # print("Adding patient with assignment record type = {}".format(type(assignment_record)))
            sr.add_patient_by_type(patient_type, assignment_record)

        result = sr.get_json()
        self.maxDiff = None
        self.assertEqual(result, exp_result)


if __name__ == '__main__':
    unittest.main()
