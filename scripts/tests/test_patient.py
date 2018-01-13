#!/usr/bin/env python3
import datetime
import unittest

from ddt import ddt, data, unpack

from scripts.summary_report_refresher.patient import Patient, convert_date
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
        ('PENDING_APPROVAL', pd.TEST_PATIENT['patientTriggers'][2]),
        ('ON_TREATMENT_ARM', pd.TEST_PATIENT['patientTriggers'][3]),
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

    # # Test the Patient.get_dates_on_off_arm method.
    # @data(
    #     (pd.PENDING_PATIENT, None, None),
    #     (pd.CURRENT_PATIENT, pd.ON_ARM_DATE, None),
    #     (pd.FORMER_PATIENT, pd.ON_ARM_DATE, pd.OFF_ARM_DATE),
    # )
    # @unpack
    # def test_get_dates_on_off_arm(self, patient_data, exp_date_on, exp_date_off):
    #     p = Patient(patient_data)
    #     (date_on, date_off) = p.get_dates_on_off_arm()
    #     self.assertEqual(date_on, exp_date_on)
    #     self.assertEqual(date_off, exp_date_off)

    # Test the Patient.get_dates_status_from_arm method.
    @data(
        (pd.REGISTERED_PATIENT, None, None, None),
        (pd.PENDING_PATIENT, None, None, 'PENDING_APPROVAL'),
        (pd.CURRENT_PATIENT, pd.ON_ARM_DATE, None, 'ON_TREATMENT_ARM'),
        (pd.FORMER_PATIENT, pd.ON_ARM_DATE, pd.OFF_ARM_DATE, 'OFF_TRIAL_DECEASED'),
        (pd.OFF_STUDY_REJOIN_PATIENT, None, None, 'PENDING_CONFIRMATION'),
        # (pd.PENDING_CONF_APPR_CONF_PATIENT, None, None, 'PENDING_CONFIRMATION'),  # not a realistic scenario
        # (pd.PENDING_ON_PENDING_PATIENT, pd.ON_ARM_DATE, pd.NEW_PENDING_CONF_DATE, 'PENDING_CONFIRMATION'),  # not a realistic scenario
        (pd.NOT_ENROLLED_PATIENT, None, None, 'OFF_TRIAL_DECEASED'),
        (pd.NOT_ELIGIBLE_PATIENT, None, None, 'NOT_ELIGIBLE'),
    )
    @unpack
    def test_get_dates_status_from_arm(self, patient_data, exp_date_on, exp_date_off, exp_status):
        p = Patient(patient_data)
        (date_on, date_off, status) = p.get_dates_status_from_arm()
        self.assertEqual(date_on, exp_date_on)
        self.assertEqual(date_off, exp_date_off)
        self.assertEqual(status, exp_status)

    # Test Patient._trigger_belongs_to_assignment method.
    @data(
        (pd.PENDING_CONF_TRIGGER, pd.PENDING_CONF_DATE, True),
        (pd.PENDING_CONF_TRIGGER, pd.PENDING_CONF_DATE - datetime.timedelta(seconds=299), True),
        (pd.PENDING_CONF_TRIGGER, pd.PENDING_CONF_DATE - datetime.timedelta(seconds=300), False),
        (pd.PENDING_CONF_TRIGGER, pd.PENDING_CONF_DATE + datetime.timedelta(seconds=1), False),
    )
    @unpack
    def test_trigger_belongs_to_assignment(self, trigger, assignment_date, exp_result):
        # assignment_date_ts = pd.datetime_to_timestamp(assignment_date)
        # result = Patient._trigger_belongs_to_assignment(trigger, assignment_date_ts)
        result = Patient._trigger_belongs_to_assignment(trigger, assignment_date)
        self.assertEqual(result, exp_result)

    # Test the Patient.get_date_assigned method.
    @data(
        (pd.REGISTERED_PATIENT, None),
        (pd.CURRENT_PATIENT, pd.ASSIGNMENT_DATE)
    )
    @unpack
    def test_get_date_assigned(self, patient_data, exp_date):
        p = Patient(patient_data)
        assd_date = p.get_date_assigned()
        self.assertEqual(assd_date, exp_date)

    # Test the Patient.get_analysis_id_and_bsn method.
    @data(
        (None, None, None),
        ([pd.MATCHING_GOOD_BIOPSY1], pd.MATCHING_ANALYSIS_ID, pd.MATCHING_BIOPSY_SEQ_NUM),
        ([pd.MATCHING_GOOD_BIOPSY2], pd.MATCHING_ANALYSIS_ID, pd.MATCHING_BIOPSY_SEQ_NUM),
        ([pd.MATCHING_GOOD_BIOPSY3], pd.MATCHING_ANALYSIS_ID, pd.MATCHING_BIOPSY_SEQ_NUM),
        ([pd.MATCHING_BAD_BIOPSY1, pd.MATCHING_GOOD_BIOPSY1], pd.MATCHING_ANALYSIS_ID, pd.MATCHING_BIOPSY_SEQ_NUM),
        ([pd.MATCHING_BAD_BIOPSY1, pd.NOMATCH_BAD_BIOPSY1, pd.MATCHING_FAILED_BIOPSY1], None, None),
        ([pd.MATCHING_BAD_BIOPSY2, pd.NOMATCH_BAD_BIOPSY2, pd.MATCHING_FAILED_BIOPSY2], None, None),
        ([pd.NOMATCH_GOOD_BIOPSY1, pd.NOMATCH_GOOD_BIOPSY3, pd.MATCHING_FAILED_BIOPSY3], None, None),
        ([pd.NOMATCH_GOOD_BIOPSY2, pd.MATCHING_GOOD_BIOPSY2], pd.MATCHING_ANALYSIS_ID, pd.MATCHING_BIOPSY_SEQ_NUM),
    )
    @unpack
    def test_get_analysis_id_and_bsn(self, biopsies, exp_analysis_id, exp_biopsy_seq_num):
        p = Patient(pd.create_patient(biopsies=biopsies))
        analysis_id, biopsy_seq_num = p.get_analysis_id_and_bsn()
        self.assertEqual(analysis_id, exp_analysis_id)
        self.assertEqual(biopsy_seq_num, exp_biopsy_seq_num)

class TestConvertDate(unittest.TestCase):
    def test(self):
        dt = pd.PENDING_CONF_DATE
        ts = pd.datetime_to_timestamp(dt)
        self.assertEqual(convert_date(ts), dt)

    def test_exc(self):
        with self.assertRaises(TypeError):
            convert_date(pd.PENDING_CONF_DATE)

if __name__ == '__main__':
    unittest.main()
