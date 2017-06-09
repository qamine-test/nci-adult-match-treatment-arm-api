#!/usr/bin/env python3
import unittest
from datetime import datetime

from bson.objectid import ObjectId
from ddt import ddt, data, unpack

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

def create_default_patient_assignment_logic(trtmtId):
    return  {
                "treatmentArmId": trtmtId,
                "treatmentArmVersion": "2015-08-06",
                "reason": "The patient contains no matching variant.",
                "patientAssignmentReasonCategory": "NO_VARIANT_MATCH"
            }


TEST_PATIENT = {
    "_id": ObjectId("55e9e33600929ab89f5499a1"),
    "patientTriggers": [
        {
            "studyId": "EAY131",
            "patientSequenceNumber": "10065",
            "stepNumber": "0",
            "patientStatus": "REGISTRATION",
            "message": "Patient registration to step 0.",
            "dateCreated": datetime(2015, 9, 4, 18, 22, 0),
            "auditDate": datetime(2015, 9, 4, 18, 30, 14)
        },
        {
            "studyId": "EAY131",
            "patientSequenceNumber": "10065",
            "stepNumber": "0",
            "patientStatus": "PENDING_CONFIRMATION",
            "dateCreated": datetime(2015, 9, 29, 21, 00, 11),
            "auditDate": datetime(2015, 9, 29, 21, 00, 12)
        },
        {
            "studyId": "EAY131",
            "patientSequenceNumber": "10065",
            "stepNumber": "0",
            "patientStatus": "PENDING_APPROVAL",
            "dateCreated": datetime(2015, 9, 30, 12, 34, 55),
            "auditDate": datetime(2015, 9, 30, 12, 34, 56)
        },
        {
            "studyId": "EAY131",
            "patientSequenceNumber": "10065",
            "stepNumber": "1",
            "patientStatus": "ON_TREATMENT_ARM",
            "message": "Patient registration to assigned treatment arm EAY131-B",
            "dateCreated": datetime(2015, 10, 5, 21, 0, 11),
            "auditDate": datetime(2015, 10, 5, 21, 0, 11)
        }
    ],
    "currentStepNumber": "1",
    "currentPatientStatus": "ON_TREATMENT_ARM",
    "patientAssignments": {
        "dateAssigned": datetime(2015, 9, 29, 21, 00, 11),
        "biopsySequenceNumber": "T-15-000078",
        "treatmentArm": TREATMENT_ARM,
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
    "treatmentArm": TREATMENT_ARM,
}


@ddt
class TestPatient(unittest.TestCase):
    @data(

    )
    @unpack
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
