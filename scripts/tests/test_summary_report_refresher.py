#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack

from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.refresher import Refresher
from scripts.summary_report_refresher.summary_report import SummaryReport
from scripts.tests.test_patient import TEST_PATIENT, create_patient_trigger

TRIGGERS_FOR_NOT_ENROLLED = ['REGISTRATION', 'PENDING_CONFIRMATION', 'PENDING_APPROVAL', 'NOT_ELIGIBLE']

PAT_STATUS_FLD = 'currentPatientStatus'
def create_patient(status, patient_trigger_types=None):
    patient_json = dict(TEST_PATIENT)
    patient_json[PAT_STATUS_FLD] = status
    # overwrite the default patientTriggers in TEST_PATIENT if caller needed something specific.
    if patient_trigger_types is not None:
        patient_json['patientTriggers'] = [create_patient_trigger(t) for t in patient_trigger_types]
    return Patient(patient_json)

# Default TreatmentArm
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

    # @data(
    #
    # )
    # @unpack
    # def test_create_assignment_record(self):
    #     pass
    #
    #
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
