#!/usr/bin/env python3
import unittest

from ddt import ddt, data, unpack

from scripts.summary_report_refresher.patient import Patient
# ******** Test Data Constants and Helper Functions to build data structures used in test cases ******** #
from scripts.tests.patient_data import TEST_PATIENT_NO_TA, TREATMENT_ARM, TEST_PATIENT


# ******** Test the Patient class in patient.py. ******** #
@ddt
class TestPatient(unittest.TestCase):
    def test_constructor_and_get(self):
        p = Patient(TEST_PATIENT)
        self.assertEqual(p.diseases, TEST_PATIENT['diseases'])
        self.assertEqual(p.treatmentArm, TEST_PATIENT['treatmentArm'])
        self.assertEqual(p.currentPatientStatus, TEST_PATIENT['currentPatientStatus'])
        self.assertEqual(p.currentStepNumber, TEST_PATIENT['currentStepNumber'])
        self.assertEqual(p.patientTriggers, TEST_PATIENT['patientTriggers'])
        self.assertEqual(p.patientAssignments, TEST_PATIENT['patientAssignments'])

    @data(
        (TEST_PATIENT, TREATMENT_ARM['version']),
        (TEST_PATIENT_NO_TA, None),
    )
    @unpack
    def test_treatment_arm_version(self, patient_json, exp_trtmt_ver):
        patient = Patient(patient_json)
        self.assertEqual(patient.treatment_arm_version(), exp_trtmt_ver)

    @data(
        ('PENDING_APPROVAL', TEST_PATIENT['patientTriggers'][3]),
        ('ON_TREATMENT_ARM', TEST_PATIENT['patientTriggers'][4]),
        ('STATUS_NOT_FOUND', None),
    )
    @unpack
    def test_find_trigger_by_status(self, status, exp_trigger):
        p = Patient(TEST_PATIENT)
        self.assertEqual(p.find_trigger_by_status(status), exp_trigger)

    @data(
        ('EAY131-Q', '2015-08-06', TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][0]['reason']),
        ('EAY131-V', '2015-08-06', TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][9]['reason']),
        ('EAY131-B', '2015-08-06', TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][8]['reason']),
        ('EAY131-B', '2015-00-00', None),
        ('EAY131-*', '2015-08-06', None),
    )
    @unpack
    def test_get_assignment_reason(self, treatment_id, treatment_version, exp_reason):
        p = Patient(TEST_PATIENT)
        self.assertEqual(p.get_assignment_reason(treatment_id, treatment_version), exp_reason)


if __name__ == '__main__':
    unittest.main()
