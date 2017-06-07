#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack

from scripts.summary_report_refresher.summary_report import SummaryReport

DEFAULT_SR = {'assignmentRecords': []}
for f in SummaryReport._SR_COUNT_FIELDS:
    DEFAULT_SR[f] = 0
DEFAULT_TA = {'_id': '1234567890',
              'treatmentId': 'EAY131-A',
              'version': '2016-08-14',
              'treatmentArmStatus': 'OPEN'}
ALL_FIELDS = SummaryReport._REQ_JSON_FIELDS


def create_json(omit_flds=None):
    if omit_flds is None:
        return DEFAULT_TA
    else:
        return dict([(f, DEFAULT_TA[f]) for f in DEFAULT_TA if f not in omit_flds])


@ddt
class TestSummaryReport(unittest.TestCase):

    @data(
        (['ALL']),
        (['version','treatmentId']),
        (['version']),
    )
    def test_constructor_with_exc(self, missing_field_list):
        if len(missing_field_list) == 1 and missing_field_list[0] == 'ALL':
            sr_json_doc = None
            missing_field_list = ALL_FIELDS
        else:
            sr_json_doc = create_json(missing_field_list)

        with self.assertRaises(Exception) as cm:
            SummaryReport(sr_json_doc)
        exc_str = str(cm.exception)
        self.assertRegex(exc_str,
                         "^The following required fields were missing from the submitted summary report JSON document:")
        for f in missing_field_list:
            self.assertTrue(f in exc_str)

    def test_get_after_normal_construction(self):
        sr = SummaryReport(create_json())
        self.assertEqual(sr._id, DEFAULT_TA['_id'])
        self.assertEqual(sr.treatmentId, DEFAULT_TA['treatmentId'])
        self.assertEqual(sr.version, DEFAULT_TA['version'])
        self.assertEqual(sr.treatmentArmStatus, DEFAULT_TA['treatmentArmStatus'])
        self.assertEqual(sr.assignmentRecords, DEFAULT_SR['assignmentRecords'])
        self.assertEqual(sr.numNotEnrolledPatient, DEFAULT_SR['numNotEnrolledPatient'])
        self.assertEqual(sr.numPendingArmApproval, DEFAULT_SR['numPendingArmApproval'])
        self.assertEqual(sr.numFormerPatients, DEFAULT_SR['numFormerPatients'])
        self.assertEqual(sr.numCurrentPatientsOnArm, DEFAULT_SR['numCurrentPatientsOnArm'])



@ddt
class self(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_sr = SummaryReport(create_json())

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
        self.test_sr.add_patient_by_type(patient_type)
        self.assertEqual(self.test_sr.numNotEnrolledPatient, not_enrolled_cnt)
        self.assertEqual(self.test_sr.numPendingArmApproval, pending_cnt)
        self.assertEqual(self.test_sr.numFormerPatients, former_cnt)
        self.assertEqual(self.test_sr.numCurrentPatientsOnArm, current_cnt)

    def test_add_with_exc(self):
        with self.assertRaises(Exception) as cm:
            self.test_sr.add_patient_by_type('invalidType')
        exc_str = str(cm.exception)
        self.assertEqual(exc_str, "Invalid patient type 'invalidType'")

if __name__ == '__main__':
    # import pprint
    # pprint.pprint(DEFAULT_SR)
    # pprint.pprint(DEFAULT_TA)
    # pprint.pprint(create_json())
    # pprint.pprint(create_json(['version','treatmentId']))
    # pprint.pprint(create_json(['version']))
    unittest.main()
