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


def create_patient_trigger(patient_status, message=None, date_created=None):
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
    if date_created is not None:
        trigger['dateCreated'] = date_created

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

ON_ARM_DATE = datetime(2015, 10, 1)
OFF_ARM_DATE = datetime(2016, 3, 1)
ASSIGNMENT_DATE = datetime(2015, 9, 29)


def create_patient(triggers=None, assignment_logics=None,
                   current_patient_status='ON_TREATMENT_ARM', treatment_arm=None):
    if triggers is None:
        triggers = DEFAULT_TRIGGERS
    if assignment_logics is None:
        assignment_logics = DEFAULT_ASSIGNMENT_LOGICS
    # NOTE:  No default value for treatment_arm because it is sometimes missing from Patient records.

    patient = {
        "_id": ObjectId("55e9e33600929ab89f5499a1"),
        "patientSequenceNumber": "14400",
        "patientTriggers": triggers,
        "currentStepNumber": "1",
        "currentPatientStatus": current_patient_status,
        "patientAssignments": {},
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

    if assignment_logics != []:
        patient['patientAssignments'] = {
            "dateAssigned": ASSIGNMENT_DATE,
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
        }
    if treatment_arm is not None:
        patient['treatmentArm'] = treatment_arm
        if current_patient_status == 'ON_TREATMENT_ARM':
            patient['patientAssignments']['treatmentArm'] = PATIENT_TREATMENT_ARM

    return patient


TEST_PATIENT_NO_TA = create_patient(current_patient_status='OFF_TRIAL', treatment_arm=None)
TEST_PATIENT = create_patient(DEFAULT_TRIGGERS, DEFAULT_ASSIGNMENT_LOGICS, 'ON_TREATMENT_ARM', PATIENT_TREATMENT_ARM)

REGISTRATION_TRIGGER = create_patient_trigger("REGISTRATION", message="Patient registration to step 0.")
PENDING_CONF_TRIGGER = create_patient_trigger("PENDING_CONFIRMATION")
PENDING_APPR_TRIGGER = create_patient_trigger("PENDING_APPROVAL")
DECEASED_TRIGGER = create_patient_trigger("OFF_TRIAL_DECEASED", date_created=OFF_ARM_DATE)
ON_ARM_TRIGGER = create_patient_trigger("ON_TREATMENT_ARM",
                                        message="Patient registration to assigned treatment arm EAY131-B",
                                        date_created=ON_ARM_DATE)

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
REGISTERED_PATIENT = create_patient(
    [
        REGISTRATION_TRIGGER,
    ],
    [],  # No assignments yet
    'REGISTERED',
    None
)
