from datetime import datetime

from bson import ObjectId


def create_patient_assignment_logic(trtmt_id, ver="2015-08-06", reason="The patient contains no matching variant.",
                                    category="NO_VARIANT_MATCH"):
    return {
        "treatmentArmId": trtmt_id,
        "treatmentArmVersion": ver,
        "reason": reason,
        "patientAssignmentReasonCategory": category
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


DEFAULT_TRIGGERS = [
        create_patient_trigger("REGISTRATION", "Patient registration to step 0."),
        create_patient_trigger("PENDING_CONFIRMATION"),
        create_patient_trigger("PENDING_APPROVAL"),
        create_patient_trigger("PENDING_APPROVAL"),
        create_patient_trigger("ON_TREATMENT_ARM", "Patient registration to assigned treatment arm EAY131-B"),
    ]

MATCHING_LOGIC = \
    create_patient_assignment_logic("EAY131-B",
                                    reason="The patient and treatment arm match on variant identifier [COSM94225,COSM14062].",
                                    category="SELECTED")

DEFAULT_ASSIGNMENT_LOGICS = [
    create_patient_assignment_logic("EAY131-Q",
                                    reason="The patient is excluded from this treatment arm because the patient has disease(s) Invasive breast carcinoma.",
                                    category="RECORD_BASED_EXCLUSION"),
    create_patient_assignment_logic("EAY131-U"),
    create_patient_assignment_logic("EAY131-F"),
    create_patient_assignment_logic("EAY131-G"),
    create_patient_assignment_logic("EAY131-H"),
    create_patient_assignment_logic("EAY131-R"),
    create_patient_assignment_logic("EAY131-E"),
    create_patient_assignment_logic("EAY131-A"),
    MATCHING_LOGIC,
    create_patient_assignment_logic("EAY131-V"),
]

PATIENT_TREATMENT_ARM = {
    "_id": "EAY131-B",  # NOTE: This identifier is in the treatmentId field in the treatmentArms collection.
    "name": "Afatinib-Her2 activating mutation",
    "version": "2015-08-06",
    "description": "Afatinib in HER2 activating mutation",
    "targetId": "750691.0",
    "targetName": "Afatinib",
    "numPatientsAssigned": 0,
    "maxPatientsAllowed": 35,
    "treatmentArmStatus": "OPEN",
}

def create_patient(triggers=None, assignment_logics=None,
                   current_patient_status='ON_TREATMENT_ARM', treatment_arm=PATIENT_TREATMENT_ARM):
    if triggers is None:
        triggers = DEFAULT_TRIGGERS
    if assignment_logics is None:
        assignment_logics = DEFAULT_ASSIGNMENT_LOGICS
    # if treatment_arm is None:
    #     treatment_arm = PATIENT_TREATMENT_ARM

    patient = {
        "_id": ObjectId("55e9e33600929ab89f5499a1"),
        "patientTriggers": triggers,
        "currentStepNumber": "1",
        "currentPatientStatus": current_patient_status,
        "patientAssignments": {
            "dateAssigned": datetime(2015, 9, 29, 21, 00, 11),
            "biopsySequenceNumber": "T-15-000078",
            "patientAssignmentStatus": "AVAILABLE",
            "patientAssignmentLogic": assignment_logics,
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

    if treatment_arm is not None:
        patient['treatmentArm'] = treatment_arm
        if current_patient_status == 'ON_TREATMENT_ARM':
            patient['patientAssignments']['treatmentArm'] = PATIENT_TREATMENT_ARM

    return patient



TEST_PATIENT_NO_TA = create_patient(current_patient_status='OFF_TRIAL', treatment_arm=None)
TEST_PATIENT = create_patient(DEFAULT_TRIGGERS, DEFAULT_ASSIGNMENT_LOGICS, 'ON_TREATMENT_ARM', PATIENT_TREATMENT_ARM)
# TEST_PATIENT_NO_TA = create_patient(DEFAULT_TRIGGERS, DEFAULT_ASSIGNMENT_LOGICS, 'OFF_TRIAL', None)
# TEST_PATIENT = create_patient(DEFAULT_TRIGGERS, DEFAULT_ASSIGNMENT_LOGICS, 'ON_TREATMENT_ARM', PATIENT_TREATMENT_ARM)

