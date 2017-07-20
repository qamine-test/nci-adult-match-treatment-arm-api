#!/usr/bin/env python3

import unittest
from datetime import datetime

from ddt import ddt, data, unpack
from mock import patch, MagicMock

from scripts.summary_report_refresher.assignment_record import AssignmentRecord
from scripts.summary_report_refresher.patient import Patient
from scripts.summary_report_refresher.refresher import Refresher
from scripts.summary_report_refresher.summary_report import SummaryReport
from scripts.tests import patient_data as pd

# ******** Test Data Constants and Helper Functions to build data structures used in test cases ******** #


def create_sr_json(**kwargs):
    sum_rpt = {'assignmentRecords': []}
    for fld in SummaryReport._SR_COUNT_FIELDS:
        sum_rpt[fld] = 0
    for (k, v) in kwargs.items():
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

TRIGGERS_FOR_NOT_ENROLLED = [pd.REGISTRATION_TRIGGER, pd.PENDING_CONF_TRIGGER, pd.PENDING_APPR_TRIGGER,
                             pd.create_patient_trigger('NOT_ELIGIBLE')]

DATE_NOW = datetime(2016, 11, 1)  # used for mocking datetime.now()


# ******** Test the Refresher class in refresher.py. ******** #
@ddt
class RefresherTest(unittest.TestCase):
    # Test the Refresher._match method.
    @data(
        (None, False),
        (SummaryReport.PENDING, True),
    )
    @unpack
    @patch('scripts.summary_report_refresher.refresher.SummaryReport')
    @patch('scripts.summary_report_refresher.refresher.AssignmentRecord')
    def test_match(self, patient_type, add_patient_by_type_expected,
                   mock_assignment_record, mock_sum_rpt):
        sr = mock_sum_rpt.return_value
        ar = mock_assignment_record.return_value

        orig_create_assignment_record = Refresher._create_assignment_record
        orig_determine_patient_classification_by_dates = Refresher._determine_patient_classification_by_dates
        Refresher._determine_patient_classification_by_dates = \
            MagicMock(name='patient_type',
                      return_value=patient_type)
        Refresher._create_assignment_record = MagicMock(name='_create_assignment_record', return_value=ar)

        try:
            patient = Patient(pd.create_patient())
            Refresher._match(patient, sr)

            self.maxDiff = None
            if add_patient_by_type_expected:
                sr.add_patient_by_type.assert_called_once_with(patient_type, ar)
            else:
                sr.add_patient_by_type.assert_not_called()
        finally:    # Because these are static methods, they must be reassigned to the original function or else
                    # their mocking will persist to other test cases.
            Refresher._create_assignment_record = orig_create_assignment_record
            Refresher._determine_patient_classification_by_dates = orig_determine_patient_classification_by_dates

    # Test the Refresher._update_summary_report method.
    @data(
        # 1. no patients associated with treatmentArm
        ([], DEFAULT_TA, create_sr_json(), []),
        # 2. only patients with no treatmentArm
        ([pd.REGISTERED_PATIENT], DEFAULT_TA, create_sr_json(), []),
        # 3. a matching patient that was considered but not enrolled
        ([pd.NOT_ENROLLED_PATIENT], DEFAULT_TA, create_sr_json(numNotEnrolledPatient=1), [pd.NOT_ENROLLED_PATIENT]),
        # 4. a matching former patient
        ([pd.FORMER_PATIENT], DEFAULT_TA, create_sr_json(numFormerPatients=1), [pd.FORMER_PATIENT]),
        # 5. a matching pending patient
        ([pd.PENDING_PATIENT], DEFAULT_TA, create_sr_json(numPendingArmApproval=1), [pd.PENDING_PATIENT]),
        # 6. a matching current patient
        ([pd.CURRENT_PATIENT], DEFAULT_TA, create_sr_json(numCurrentPatientsOnArm=1), [pd.CURRENT_PATIENT]),
        # 7. a matching current and former patient, plus one non-matching patient
        ([pd.CURRENT_PATIENT, pd.REGISTERED_PATIENT, pd.FORMER_PATIENT],
         DEFAULT_TA,
         create_sr_json(numCurrentPatientsOnArm=1, numFormerPatients=1),
         [pd.CURRENT_PATIENT, pd.FORMER_PATIENT]),
        # 8. two matching current patients (same patient), one pending patient, plus two non-matching patients
        ([pd.REGISTERED_PATIENT, pd.CURRENT_PATIENT, pd.PENDING_PATIENT, pd.CURRENT_PATIENT, pd.REGISTERED_PATIENT],
         DEFAULT_TA,
         create_sr_json(numCurrentPatientsOnArm=1, numPendingArmApproval=1),
         [pd.CURRENT_PATIENT, pd.PENDING_PATIENT]),
        # 9.
        ([pd.PATIENT_ON_ARM_TWICE2, pd.PATIENT_ON_ARM_TWICE1, pd.CURRENT_PATIENT,
          pd.PENDING_PATIENT, pd.FORMER_PATIENT],
         DEFAULT_TA,
         create_sr_json(numCurrentPatientsOnArm=1, numPendingArmApproval=1, numFormerPatients=1,
                        numNotEnrolledPatient=1),
         [pd.PATIENT_ON_ARM_TWICE2, pd.CURRENT_PATIENT, pd.PENDING_PATIENT, pd.FORMER_PATIENT]),
    )
    @unpack
    @patch('scripts.summary_report_refresher.refresher.logging')
    @patch('scripts.summary_report_refresher.refresher.PatientAccessor')
    @patch('scripts.summary_report_refresher.refresher.TreatmentArmsAccessor')
    def test_update_summary_report(self, patients, ta_data_for_sum_rpt, expected_sum_rpt_json, expected_ar_patients,
                                   mock_ta_accessor, mock_patient_accessor, mock_logging):

        self.maxDiff = None

        ar_records = []
        for patient in expected_ar_patients:
            assmt_rec = Refresher._create_assignment_record(Patient(patient), ta_data_for_sum_rpt['treatmentId'])
            ar_records.append(assmt_rec.get_json())
        expected_sum_rpt_json['assignmentRecords'] = ar_records

        # Set up the mocked PatientAcessor
        pa_instance = mock_patient_accessor.return_value
        pa_instance.get_patients_by_treatment_arm_id.return_value = patients

        # Set up the mocked TreatmentArmsAccessor
        taa_instance = mock_ta_accessor.return_value
        taa_instance.update_summary_report = lambda _id, json: self.assertEqual(json, expected_sum_rpt_json)

        sum_rpt = SummaryReport(ta_data_for_sum_rpt)
        r = Refresher()
        r._update_summary_report(sum_rpt)

    # Test the Refresher.run method.
    @data(
        ([True, True, True]),
        ([True, False, True, True]),
    )
    @patch('scripts.summary_report_refresher.refresher.logging')
    @patch('scripts.summary_report_refresher.refresher.PatientAccessor')
    @patch('scripts.summary_report_refresher.refresher.TreatmentArmsAccessor')
    def test_run(self, update_summary_rpt_rets, mock_ta_accessor, mock_patient_accessor, mock_logging):
        self.maxDiff = None

        taa_instance = mock_ta_accessor.return_value
        taa_instance.get_arms_for_summary_report_refresh.return_value = [DEFAULT_TA] * len(update_summary_rpt_rets)

        r = Refresher()
        r._update_summary_report = MagicMock(side_effect=update_summary_rpt_rets)
        r.run()

        mock_logger = mock_logging.getLogger()
        mock_logger.info.assert_called()
        if False in update_summary_rpt_rets:
            mock_logger.error.assert_called()
            mock_logger.exception.assert_called()
        else:
            mock_logger.error.assert_not_called()
            mock_logger.exception.assert_not_called()

    # Test the Refresher._determine_patient_classification_by_dates method.
    @data(
        (None, None, None, None, None),
        (pd.ASSIGNMENT_DATE, None, None, None, SummaryReport.NOT_ENROLLED),
        (pd.ASSIGNMENT_DATE, None, None, 'PENDING_APPROVAL', SummaryReport.PENDING),
        (pd.ASSIGNMENT_DATE, None, None, 'PENDING_CONFIRMATION', SummaryReport.PENDING),
        (pd.ASSIGNMENT_DATE, pd.ON_ARM_DATE, None, 'ON_TREATMENT_ARM', SummaryReport.CURRENT),
        (pd.ASSIGNMENT_DATE, pd.ON_ARM_DATE, pd.OFF_ARM_DATE, 'OFF_TRIAL', SummaryReport.FORMER),
    )
    @unpack
    @patch('scripts.summary_report_refresher.refresher.AssignmentRecord')
    def test_determine_patient_classification(self, ar_date_sel, ar_date_on_arm, ar_date_off_arm, ar_status,
                                              expected_patient_type, mock_ar):
        mock_ar_inst = mock_ar.return_value
        mock_ar_inst.date_selected = ar_date_sel
        mock_ar_inst.date_on_arm = ar_date_on_arm
        mock_ar_inst.date_off_arm = ar_date_off_arm
        mock_ar_inst.assignment_status_outcome = ar_status

        patient_type = Refresher._determine_patient_classification_by_dates(mock_ar_inst)
        self.assertEqual(patient_type, expected_patient_type)

    @data(
        (pd.PENDING_PATIENT, pd.MATCHING_LOGIC['treatmentArmId'],
         [pd.PENDING_PATIENT['patientSequenceNumber'], pd.MATCHING_LOGIC['treatmentArmVersion'],
          pd.PENDING_PATIENT['currentPatientStatus'], pd.MATCHING_LOGIC['reason'],
          pd.PENDING_PATIENT['patientAssignments']['stepNumber'], pd.PENDING_PATIENT['diseases'],
          pd.MATCHING_ANALYSIS_ID, pd.PENDING_PATIENT['patientAssignmentIdx'],
          pd.PENDING_PATIENT['patientAssignments']['dateAssigned'], None, None
          ]),
        (pd.CURRENT_PATIENT, pd.MATCHING_LOGIC['treatmentArmId'],
         [pd.CURRENT_PATIENT['patientSequenceNumber'], pd.MATCHING_LOGIC['treatmentArmVersion'],
          pd.CURRENT_PATIENT['currentPatientStatus'], pd.MATCHING_LOGIC['reason'],
          pd.CURRENT_PATIENT['patientAssignments']['stepNumber'], pd.CURRENT_PATIENT['diseases'],
          pd.MATCHING_ANALYSIS_ID, pd.CURRENT_PATIENT['patientAssignmentIdx'],
          pd.CURRENT_PATIENT['patientAssignments']['dateAssigned'],
          pd.ON_ARM_DATE, None
          ]),
        (pd.FORMER_PATIENT, pd.MATCHING_LOGIC['treatmentArmId'],
         [pd.FORMER_PATIENT['patientSequenceNumber'], pd.MATCHING_LOGIC['treatmentArmVersion'],
          pd.FORMER_PATIENT['currentPatientStatus'], pd.MATCHING_LOGIC['reason'],
          pd.FORMER_PATIENT['patientAssignments']['stepNumber'], pd.FORMER_PATIENT['diseases'],
          pd.MATCHING_ANALYSIS_ID, pd.FORMER_PATIENT['patientAssignmentIdx'],
          pd.FORMER_PATIENT['patientAssignments']['dateAssigned'],
          pd.ON_ARM_DATE, pd.OFF_ARM_DATE
          ])
    )
    @unpack
    def test_create_assignment_record(self, patient, trtmt_id, ar_constructor_args):
        exp_ar = AssignmentRecord(*ar_constructor_args)
        ar = Refresher._create_assignment_record(Patient(patient), trtmt_id)

        self.assertEqual(ar.patient_sequence_number, exp_ar.patient_sequence_number)
        self.assertEqual(ar.treatment_arm_version, exp_ar.treatment_arm_version)
        self.assertEqual(ar.assignment_status_outcome, exp_ar.assignment_status_outcome)
        self.assertEqual(ar.analysis_id, exp_ar.analysis_id)
        self.assertEqual(ar.patient_assmt_idx, exp_ar.patient_assmt_idx)
        self.assertEqual(ar.date_selected, exp_ar.date_selected)
        self.assertEqual(ar.date_on_arm, exp_ar.date_on_arm)
        self.assertEqual(ar.date_off_arm, exp_ar.date_off_arm)
        self.assertEqual(ar.step_number, exp_ar.step_number)
        self.assertEqual(ar.diseases, exp_ar.diseases)
        self.assertEqual(ar.assignment_reason, exp_ar.assignment_reason)


if __name__ == '__main__':
    unittest.main()
