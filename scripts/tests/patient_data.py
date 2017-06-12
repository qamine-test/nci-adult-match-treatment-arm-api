from datetime import datetime

from bson import ObjectId


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
