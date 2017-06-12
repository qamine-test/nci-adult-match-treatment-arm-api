#!/usr/bin/env python3

import unittest
from datetime import datetime
from ddt import ddt, data, unpack
from mock import patch

from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.refresher import Refresher
from scripts.summary_report_refresher.summary_report import SummaryReport
from scripts.tests.patient_data import create_patient, create_patient_trigger, create_patient_assignment_logic, TEST_PATIENT, PATIENT_TREATMENT_ARM, MATCHING_LOGIC
from config import log  # contains required log configuration; ignore Codacy complaints about unused code

# ******** Test Data Constants and Helper Functions to build data structures used in test cases ******** #
REGISTRATION_TRIGGER = create_patient_trigger("REGISTRATION", "Patient registration to step 0.")
PENDING_CONF_TRIGGER = create_patient_trigger("PENDING_CONFIRMATION")
PENDING_APPR_TRIGGER = create_patient_trigger("PENDING_APPROVAL")
DECEASED_TRIGGER = create_patient_trigger("OFF_TRIAL_DECEASED")
ON_ARM_TRIGGER = create_patient_trigger("ON_TREATMENT_ARM", "Patient registration to assigned treatment arm EAY131-B")

NOT_ENROLLED_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, DECEASED_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-E"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    'OFF_TRIAL_DECEASED',
    PATIENT_TREATMENT_ARM
)

FORMER_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER, DECEASED_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-A"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    'OFF_TRIAL_DECEASED',
    PATIENT_TREATMENT_ARM
)

PENDING_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-S"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-E"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    'PENDING_APPROVAL',
    PATIENT_TREATMENT_ARM
)

CURRENT_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-H"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-G"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    'ON_TREATMENT_ARM',
    PATIENT_TREATMENT_ARM
)
NONE_PATIENT = create_patient(
    [
        REGISTRATION_TRIGGER,
        PENDING_CONF_TRIGGER,
        create_patient_trigger("PENDING_OFF_STUDY"),
        create_patient_trigger("OFF_TRIAL_NO_TA_AVAILABLE"),
    ],
    [
        create_patient_assignment_logic("EAY131-A"),
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    'OFF_TRIAL_NO_TA_AVAILABLE',
    None
)


def create_sr_json(**kwargs):
    sum_rpt = {'assignmentRecords': []}
    for fld in SummaryReport._SR_COUNT_FIELDS:
        sum_rpt[fld] = 0
    for (k,v) in kwargs.items():
        if k in sum_rpt:
            sum_rpt[k] = v
        else:
            raise Exception("Invalid keyword argument '{k}' pass to {fn}".format(k=k, fn=__name__))
    return sum_rpt


# Default TreatmentArm
DEFAULT_TA = {'_id': '2234567890',
              'treatmentId': 'EAY131-A',
              'version': '2016-08-15',
              'treatmentArmStatus': 'OPEN'}

MATCHING_TA = {
    "_id": "2234567899",
    'treatmentId': 'EAY131-B',
    "version": "2015-08-06",
    "treatmentArmStatus": "OPEN",
}

# Indices for the expected results in test cases below
CURR_IDX = 0
PEND_IDX = 1
FORM_IDX = 2
NOEN_IDX = 3
AREC_IDX = 4

TRIGGERS_FOR_NOT_ENROLLED = [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER,
                             create_patient_trigger('NOT_ELIGIBLE')]

DATE_NOW = datetime(2016, 11, 1)  # used for mocking datetime.now()


# def create_patient(status, patient_trigger_types=None):
#     patient_json = dict(TEST_PATIENT)
#     patient_json['currentPatientStatus'] = status
#     # overwrite the default patientTriggers in TEST_PATIENT if caller needed something specific.
#     if patient_trigger_types is not None:
#         patient_json['patientTriggers'] = [create_patient_trigger(t) for t in patient_trigger_types]
#     return Patient(patient_json)


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
        patient = Patient(create_patient(current_patient_status=patient_status))
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
        #1. no patients associated with treatmentArm
        ([], DEFAULT_TA, create_sr_json(), []),
        #2. only patients with no treatmentArm
        ([NONE_PATIENT], DEFAULT_TA, create_sr_json(), []),
        #3. a matching patient that was considered but not enrolled
        ([NOT_ENROLLED_PATIENT], DEFAULT_TA, create_sr_json(numNotEnrolledPatient=1), [NOT_ENROLLED_PATIENT]),
        #4. a matching former patient
        ([FORMER_PATIENT], DEFAULT_TA, create_sr_json(numFormerPatients=1), [FORMER_PATIENT]),
        # 5. a matching pending patient
        ([PENDING_PATIENT], DEFAULT_TA, create_sr_json(numPendingArmApproval=1), [PENDING_PATIENT]),
        # 6. a matching current patient
        ([CURRENT_PATIENT], DEFAULT_TA, create_sr_json(numCurrentPatientsOnArm=1), [CURRENT_PATIENT]),
        # 7. a matching current and former patient, plus one non-matching patient
        ([CURRENT_PATIENT, NONE_PATIENT, FORMER_PATIENT],
         DEFAULT_TA,
         create_sr_json(numCurrentPatientsOnArm=1, numFormerPatients=1),
         [CURRENT_PATIENT, FORMER_PATIENT]),
        # 8. two matching current patients, one pending patient, plus two non-matching patients
        ([NONE_PATIENT, CURRENT_PATIENT, PENDING_PATIENT, CURRENT_PATIENT, NONE_PATIENT],
         DEFAULT_TA,
         create_sr_json(numCurrentPatientsOnArm=2, numPendingArmApproval=1),
         [CURRENT_PATIENT, PENDING_PATIENT, CURRENT_PATIENT]),
    )
    @unpack
    @patch('scripts.summary_report_refresher.refresher.PatientAccessor')
    @patch('scripts.summary_report_refresher.refresher.TreatmentArmsAccessor')
    def test_update_summary_report(self, patients, ta_data_for_sum_rpt, expected_sum_rpt_json, ar_patients,
                                   mock_ta_accessor, mock_patient_accessor):

        self.maxDiff = None

        ar_records = []
        for i, patient in enumerate(ar_patients):
            assmt_rec = Refresher._create_assignment_record(Patient(patient), ta_data_for_sum_rpt['treatmentId'])
            ar_records.append(assmt_rec.get_json(i))
        expected_sum_rpt_json['assignmentRecords'] = ar_records

        #print( "test_update_summary_report patient count = {c}".format(c=len(patients)))

        pa_instance = mock_patient_accessor.return_value
        pa_instance.get_patients_by_treatment_arm_id.return_value = patients

        taa_instance = mock_ta_accessor.return_value
        taa_instance.update_summary_report = lambda _id, json: self.assertEqual(json, expected_sum_rpt_json)

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
        if trigger_types is not None:
            patient = create_patient(current_patient_status=patient_status, triggers=trigger_types)
        else:
            patient = create_patient(current_patient_status=patient_status)
        patient_type = Refresher._determine_patient_classification(Patient(patient))
        self.assertEqual(patient_type, expected_patient_type)


if __name__ == '__main__':
    unittest.main()
