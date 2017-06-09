#!/usr/bin/env python3

import unittest

from ddt import ddt, data, unpack
from mock import patch

from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.refresher import Refresher
from scripts.summary_report_refresher.summary_report import SummaryReport
from scripts.tests.test_patient import TEST_PATIENT, create_patient_trigger
from scripts.tests.test_summary_report import DEFAULT_SR

# ******** Test Data Constants and Helper Functions to build data structures used in test cases ******** #

# Default TreatmentArm
DEFAULT_TA = {'_id': '2234567890',
              'treatmentId': 'EAY131-A',
              'version': '2016-08-15',
              'treatmentArmStatus': 'OPEN'}

# Indices for the expected results in test cases below
CURR_IDX = 0
PEND_IDX = 1
FORM_IDX = 2
NOEN_IDX = 3
AREC_IDX = 4

TRIGGERS_FOR_NOT_ENROLLED = ['REGISTRATION', 'PENDING_CONFIRMATION', 'PENDING_APPROVAL', 'NOT_ELIGIBLE']


def create_patient(status, patient_trigger_types=None):
    patient_json = dict(TEST_PATIENT)
    patient_json['currentPatientStatus'] = status
    # overwrite the default patientTriggers in TEST_PATIENT if caller needed something specific.
    if patient_trigger_types is not None:
        patient_json['patientTriggers'] = [create_patient_trigger(t) for t in patient_trigger_types]
    return Patient(patient_json)


# ******** Test the Refresher class in refresher.py. ******** #
@ddt
class RefresherTest(unittest.TestCase):
    # Test the Refresher._match method.
    @data(
        ('UNKNOWN_STATUS', DEFAULT_TA, [0, 0, 0, 0, 0]),
        ('ON_TREATMENT_ARM', DEFAULT_TA, [1, 0, 0, 0, 1]),
        ('PENDING_APPROVAL', DEFAULT_TA, [0, 1, 0, 0, 1]),
    )
    @unpack
    def test_match(self, patient_status, sum_rpt_data, exp_results):
        sr = SummaryReport(sum_rpt_data)
        patient = create_patient(patient_status)
        Refresher._match(patient, sr)

        self.maxDiff = None
        self.assertEqual(len(sr.assignmentRecords), exp_results[AREC_IDX])
        self.assertEqual(sr.numNotEnrolledPatient, exp_results[NOEN_IDX])
        self.assertEqual(sr.numPendingArmApproval, exp_results[PEND_IDX])
        self.assertEqual(sr.numFormerPatients, exp_results[FORM_IDX])
        self.assertEqual(sr.numCurrentPatientsOnArm, exp_results[CURR_IDX])

    # Test the Refresher.create_assignment_record method.
    # @data(
    #
    # )
    # @unpack
    # def test_create_assignment_record(self):
    #     pass
    #
    #

    # Test the Refresher._update_summary_report method.
    @data(
        ([], DEFAULT_TA, DEFAULT_SR),  # no patients associated with treatmentArm
    )
    @unpack
    @patch('scripts.summary_report_refresher.refresher.PatientAccessor')
    @patch('scripts.summary_report_refresher.refresher.TreatmentArmsAccessor')
    def test_update_summary_report(self, patients, ta_data_for_sum_rpt, expected_sum_rpt_json,
                                   mock_ta_accessor, mock_patient_accessor):
        taa_instance = mock_ta_accessor.return_value
        taa_instance.get_patients_by_treatment_arm_id.return_value = patients

        pa_instance = mock_patient_accessor.return_value
        pa_instance.update_summary_report = lambda s, _id, json: self.assertEqual(json, expected_sum_rpt_json)

        sum_rpt = SummaryReport(ta_data_for_sum_rpt)
        r = Refresher()
        r._update_summary_report(sum_rpt)

    # Test the Refresher._determine_patient_classification method.
    @data(
        ('REGISTRATION', None, None),
        ('OFF_TRIAL_REGISTRATION_ERROR', None, None),
        ('PENDING_CONFIRMATION', None, None),
        ('PENDING_OFF_STUDY', None, None),
        ('RB_ORDER_REQUESTED', None, None),
        ('RB_RESULT_RECEIVED', None, None),
        ('ON_TREATMENT_ARM', None, SummaryReport.CURRENT),
        ('PENDING_APPROVAL', None, SummaryReport.PENDING),
        ('OFF_TRIAL', None, SummaryReport.FORMER),
        ('REJOIN_REQUESTED', None, SummaryReport.FORMER),
        ('OFF_TRIAL_DECEASED', None, SummaryReport.FORMER),
        ('OFF_TRIAL_DECEASED', None, SummaryReport.FORMER),
        ('REJOIN_REQUESTED', TRIGGERS_FOR_NOT_ENROLLED, SummaryReport.NOT_ENROLLED),
        ('OFF_TRIAL_DECEASED', TRIGGERS_FOR_NOT_ENROLLED, SummaryReport.NOT_ENROLLED),
        ('OFF_TRIAL_DECEASED', TRIGGERS_FOR_NOT_ENROLLED, SummaryReport.NOT_ENROLLED),
    )
    @unpack
    def test_determine_patient_classification(self, patient_status, trigger_types, expected_patient_type):
        patient = create_patient(patient_status, trigger_types)
        patient_type = Refresher._determine_patient_classification(patient)
        self.assertEqual(patient_type, expected_patient_type)


if __name__ == '__main__':
    unittest.main()
