#!/usr/bin/env python3
import unittest
from datetime import datetime

from bson.objectid import ObjectId
from ddt import ddt, data, unpack

from scripts.summary_report_refresher.patient import Patient

# ******** Test Data Constants and Helper Functions to build data structures used in test cases ******** #

def create_default_patient_assignment_logic(trtmt_id):
    return {
        "treatmentArmId": trtmt_id,
        "treatmentArmVersion": "2015-08-06",
        "reason": "The patient contains no matching variant.",
        "patientAssignmentReasonCategory": "NO_VARIANT_MATCH"
    }


def create_patient_trigger(patient_status, message=None):
    trigger = {
        "studyId": "EAY131",
        "patientSequenceNumber": "10065",
        "stepNumber": "0",
        "patientStatus": patient_status,
        "dateCreated": datetime(2015, 9, 4, 18, 22, 0),
        "auditDate": datetime(2015, 9, 4, 18, 30, 14)
    }
    if message is not None:
        trigger['message'] = message
    return trigger


TEST_PATIENT_NO_TA = {
    "_id": ObjectId("55e9e33600929ab89f5499a1"),
    "patientTriggers": [
        create_patient_trigger("REGISTRATION", "Patient registration to step 0."),
        create_patient_trigger("PENDING_CONFIRMATION"),
        create_patient_trigger("PENDING_APPROVAL"),
        create_patient_trigger("PENDING_APPROVAL"),
        create_patient_trigger("ON_TREATMENT_ARM", "Patient registration to assigned treatment arm EAY131-B"),
    ],
    "currentStepNumber": "1",
    "currentPatientStatus": "ON_TREATMENT_ARM",
    "patientAssignments": {
        "dateAssigned": datetime(2015, 9, 29, 21, 00, 11),
        "biopsySequenceNumber": "T-15-000078",
        # "treatmentArm": treatment_arm,
        "patientAssignmentStatus": "AVAILABLE",
        "patientAssignmentLogic": [
            {
                "treatmentArmId": "EAY131-Q",
                "treatmentArmVersion": "2015-08-06",
                "reason": "The patient is excluded from this treatment arm because the patient has disease(s) Invasive breast carcinoma.",
                "patientAssignmentReasonCategory": "RECORD_BASED_EXCLUSION"
            },
            create_default_patient_assignment_logic("EAY131-U"),
            create_default_patient_assignment_logic("EAY131-F"),
            create_default_patient_assignment_logic("EAY131-G"),
            create_default_patient_assignment_logic("EAY131-H"),
            create_default_patient_assignment_logic("EAY131-R"),
            create_default_patient_assignment_logic("EAY131-E"),
            create_default_patient_assignment_logic("EAY131-A"),
            {
                "treatmentArmId": "EAY131-B",
                "treatmentArmVersion": "2015-08-06",
                "reason": "The patient and treatment arm match on variant identifier [COSM94225,COSM14062].",
                "patientAssignmentReasonCategory": "SELECTED"
            },
            create_default_patient_assignment_logic("EAY131-V"),
        ],
        "patientAssignmentStatusMessage": "Patient registration to assigned treatment arm EAY131-B",
        "stepNumber": "0",
        "patientAssignmentMessages": [
            {
                "patientSequenceNumber": "10065",
                "treatmentArmId": "EAY131-B",
                "treatmentArmName": "Afatinib in HER2 Activating Mutation",
                "status": "ON_TREATMENT_ARM",
                "message": "Patient registration to assigned treatment arm EAY131-B",
                "stepNumber": "1"
            }
        ],
        "dateConfirmed": datetime(2015, 9, 30, 12, 34, 55)
    },
    "diseases": [
        {
            "_id": "10006190",
            "ctepCategory": "Breast Neoplasm",
            "ctepSubCategory": "Breast Cancer - Invasive",
            "ctepTerm": "Invasive breast carcinoma",
            "shortName": "Invasive breast carcinoma"
        }
    ],
    # "treatmentArm": treatment_arm,
}

TREATMENT_ARM = {
    "_id": "EAY131-B",
    "name": "Afatinib-Her2 activating mutation",
    "version": "2015-08-06",
    "description": "Afatinib in HER2 activating mutation",
    "targetId": "750691.0",
    "targetName": "Afatinib",
    "numPatientsAssigned": 0,
    "maxPatientsAllowed": 35,
    "treatmentArmStatus": "OPEN",
}

TEST_PATIENT = dict(TEST_PATIENT_NO_TA)
TEST_PATIENT['treatmentArm'] = TREATMENT_ARM
TEST_PATIENT['patientAssignments']['treatmentArm'] = TREATMENT_ARM


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
