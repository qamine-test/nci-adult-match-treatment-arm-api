#!/usr/bin/env python3
import unittest

from ddt import ddt, data, unpack

from scripts.summary_report_refresher.patient import Patient
from scripts.tests import patient_data as pd


# ******** Test the Patient class in patient.py. ******** #
@ddt
class TestPatient(unittest.TestCase):
    # Test the Patient constructor and getter methods.
    def test_constructor_and_get(self):
        p = Patient(pd.TEST_PATIENT)
        self.assertEqual(p.diseases, pd.TEST_PATIENT['diseases'])
        self.assertEqual(p.treatmentArm, pd.TEST_PATIENT['treatmentArm'])
        self.assertEqual(p.currentPatientStatus, pd.TEST_PATIENT['currentPatientStatus'])
        self.assertEqual(p.currentStepNumber, pd.TEST_PATIENT['currentStepNumber'])
        self.assertEqual(p.patientTriggers, pd.TEST_PATIENT['patientTriggers'])
        self.assertEqual(p.patientAssignments, pd.TEST_PATIENT['patientAssignments'])
        self.assertEqual(p.patientAssignmentIdx, pd.TEST_PATIENT['patientAssignmentIdx'])
        self.assertEqual(p.get_patient_assignment_step_number(), pd.DEFAULT_PAT_ASSNMNT_STEP_NUM)

    # Test the Patient.treatment_arm_version method.
    @data(
        (pd.TEST_PATIENT, pd.PATIENT_TREATMENT_ARM['version']),
        (pd.TEST_PATIENT_NO_TA, None),
    )
    @unpack
    def test_treatment_arm_version(self, patient_json, exp_trtmt_ver):
        patient = Patient(patient_json)
        self.assertEqual(patient.treatment_arm_version(), exp_trtmt_ver)

    # Test the Patient.find_trigger_by_status method.
    @data(
        ('PENDING_APPROVAL', pd.TEST_PATIENT['patientTriggers'][3]),
        ('ON_TREATMENT_ARM', pd.TEST_PATIENT['patientTriggers'][4]),
        ('STATUS_NOT_FOUND', None),
    )
    @unpack
    def test_find_trigger_by_status(self, status, exp_trigger):
        p = Patient(pd.TEST_PATIENT)
        self.assertEqual(p.find_trigger_by_status(status), exp_trigger)

    # Test the Patient.get_assignment_reason method.
    @data(
        ('EAY131-Q', '2015-08-06', pd.TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][0]['reason']),
        ('EAY131-V', '2015-08-06', pd.TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][9]['reason']),
        ('EAY131-B', '2015-08-06', pd.TEST_PATIENT['patientAssignments']['patientAssignmentLogic'][8]['reason']),
        ('EAY131-B', '2015-00-00', None),
        ('EAY131-*', '2015-08-06', None),
    )
    @unpack
    def test_get_assignment_reason(self, treatment_id, treatment_version, exp_reason):
        p = Patient(pd.TEST_PATIENT)
        self.assertEqual(p.get_assignment_reason(treatment_id, treatment_version), exp_reason)

    # Test the Patient.get_dates_on_off_arm method.
    @data(
        (pd.PENDING_PATIENT, None, None),
        (pd.CURRENT_PATIENT, pd.ON_ARM_DATE, None),
        (pd.FORMER_PATIENT, pd.ON_ARM_DATE, pd.OFF_ARM_DATE),
    )
    @unpack
    def test_get_dates_on_off_arm(self, patient_data, exp_date_on, exp_date_off):
        p = Patient(patient_data)
        (date_on, date_off) = p.get_dates_on_off_arm()
        self.assertEqual(date_on, exp_date_on)
        self.assertEqual(date_off, exp_date_off)

    # Test the Patient.get_date_assigned method.
    @data(
        (pd.REGISTERED_PATIENT, None),
        (pd.CURRENT_PATIENT, pd.ASSIGNMENT_DATE)
    )
    @unpack
    def test_(self, patient_data, exp_date):
        p = Patient(patient_data)
        assd_date = p.get_date_assigned()
        self.assertEqual(assd_date, exp_date)

    # Test the Patient.get_analysis_id method.
    @data(
        (None, None),
        ([pd.MATCHING_GOOD_BIOPSY1], pd.MATCHING_ANALYSIS_ID),
        ([pd.MATCHING_GOOD_BIOPSY2], pd.MATCHING_ANALYSIS_ID),
        ([pd.MATCHING_GOOD_BIOPSY3], pd.MATCHING_ANALYSIS_ID),
        ([pd.MATCHING_BAD_BIOPSY1, pd.MATCHING_GOOD_BIOPSY1], pd.MATCHING_ANALYSIS_ID),
        ([pd.MATCHING_BAD_BIOPSY1, pd.NOMATCH_BAD_BIOPSY1, pd.MATCHING_FAILED_BIOPSY1], None),
        ([pd.MATCHING_BAD_BIOPSY2, pd.NOMATCH_BAD_BIOPSY2, pd.MATCHING_FAILED_BIOPSY2], None),
        ([pd.NOMATCH_GOOD_BIOPSY1, pd.NOMATCH_GOOD_BIOPSY3, pd.MATCHING_FAILED_BIOPSY3], None),
        ([pd.NOMATCH_GOOD_BIOPSY2, pd.MATCHING_GOOD_BIOPSY2], pd.MATCHING_ANALYSIS_ID),
    )
    @unpack
    def test_get_analysis_id(self, biopsies, exp_analysis_id):
        p = Patient(pd.create_patient(biopsies=biopsies))
        analysis_id = p.get_analysis_id()
        self.assertEqual(analysis_id, exp_analysis_id)


if __name__ == '__main__':
    unittest.main()
