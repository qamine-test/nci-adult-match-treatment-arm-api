from datetime import datetime, timedelta, timezone


def create_patient_assignment_logic(trtmt_id, version="2015-08-06", reason="The patient contains no matching variant.",
                                    category="NO_VARIANT_MATCH"):
    return {
        "treatmentArmId": trtmt_id,
        "treatmentArmVersion": version,
        "reason": reason,
        "patientAssignmentReasonCategory": category
    }


def datetime_to_timestamp(dt):
    # Multiply by 1000 because MongoDB timestamps include milliseconds.
    return {"$date": int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)}


ASSIGNMENT_DATE = datetime(2015, 9, 29)
PENDING_CONF_DATE = datetime(2015, 9, 29, 0, 0, 1)
PENDING_OFF_STUDY_DATE = datetime(2015, 9, 12, 10, 10, 10)
PENDING_APPR_DATE = datetime(2015, 9, 30, 0, 1)
PENDING_APPR_DATE2 = datetime(2015, 9, 30, 12, 1)
ON_ARM_DATE = datetime(2015, 10, 1)
OFF_ARM_DATE = datetime(2016, 3, 1)


def create_patient_trigger(patient_status, message=None, date_created=None, patient_seq_num="10065", step_number="0"):
    trigger = {
        "studyId": "EAY131",
        "patientSequenceNumber": patient_seq_num,
        "stepNumber": step_number,
        "patientStatus": patient_status,
        "dateCreated": datetime_to_timestamp(datetime(2015, 9, 4, 18, 22, 0)),
        "auditDate": datetime_to_timestamp(datetime(2015, 9, 4, 18, 30, 14))
    }

    if message is not None:
        trigger['message'] = message
    if date_created is not None:
        trigger['dateCreated'] = datetime_to_timestamp(date_created)

    return trigger


REGISTRATION_TRIGGER = create_patient_trigger("REGISTRATION", message="Patient registration to step 0.")
PENDING_CONF_TRIGGER = create_patient_trigger("PENDING_CONFIRMATION", date_created=PENDING_CONF_DATE)
PENDING_OFF_STUDY_TRIGGER = create_patient_trigger("PENDING_OFF_STUDY", date_created=PENDING_OFF_STUDY_DATE)
PENDING_APPR_TRIGGER = create_patient_trigger("PENDING_APPROVAL", date_created=PENDING_APPR_DATE)
NOT_ELIGIBLE_TRIGGER = create_patient_trigger("NOT_ELIGIBLE", date_created=OFF_ARM_DATE)
OFF_TRIAL_TRIGGER = create_patient_trigger("OFF_TRIAL", date_created=OFF_ARM_DATE)
DECEASED_TRIGGER = create_patient_trigger("OFF_TRIAL_DECEASED", date_created=OFF_ARM_DATE)
COMPASSIONATE_CARE_TRIGGER = create_patient_trigger("COMPASSIONATE_CARE", date_created=OFF_ARM_DATE)
PROGRESSION_REBIOPSY_TRIGGER = create_patient_trigger("PROGRESSION_REBIOPSY", date_created=OFF_ARM_DATE,
                                                      step_number="2")
ON_ARM_TRIGGER = create_patient_trigger("ON_TREATMENT_ARM",
                                        message="Patient registration to assigned treatment arm EAY131-B",
                                        date_created=ON_ARM_DATE, step_number="1")
DEFAULT_TRIGGERS = [
        REGISTRATION_TRIGGER,
        PENDING_CONF_TRIGGER,
        PENDING_APPR_TRIGGER,
        # create_patient_trigger("PENDING_APPROVAL", date_created=PENDING_APPR_DATE2),
        ON_ARM_TRIGGER,
    ]

PATIENT_TREATMENT_ARM = {
    "treatmentArmId": "EAY131-B",
    "name": "Afatinib-Her2 activating mutation",
    "version": "2015-08-06",
    "description": "Afatinib in HER2 activating mutation",
    "targetId": "750691.0",
    "targetName": "Afatinib",
    "numPatientsAssigned": 0,
    "maxPatientsAllowed": 35,
    "treatmentArmStatus": "OPEN",
}
MATCHING_LOGIC = \
    create_patient_assignment_logic(PATIENT_TREATMENT_ARM["treatmentArmId"],
                                    version=PATIENT_TREATMENT_ARM["version"],
                                    reason="The patient and treatment arm match on variant identifier "
                                           "[COSM94225,COSM14062].",
                                    category="SELECTED")

DEFAULT_ASSIGNMENT_LOGICS = [
    create_patient_assignment_logic("EAY131-Q",
                                    reason="The patient is excluded from this treatment arm because the patient has "
                                           "disease(s) Invasive breast carcinoma.",
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


def create_next_generation_sequence(status, job_name):
    return {
        'status': status,
        'ionReporterResults': {'jobName': job_name}
    }
MATCHING_ANALYSIS_ID = "Confirmed Analysis ID"
CONFIRMED_NEXT_GEN_SEQ = create_next_generation_sequence("CONFIRMED", MATCHING_ANALYSIS_ID)
NOT_CONFIRMED_NEXT_GEN_SEQ = create_next_generation_sequence("not confirmed", "unconfirmed analysis ID")


def create_biopsy(biopsy_seq_num, failure, next_gen_seqs):
    """Only create the fields of the biopsy that we care about."""
    return {
        'biopsySequenceNumber': biopsy_seq_num,
        'failure': failure,
        'nextGenerationSequences': next_gen_seqs,
    }


MATCHING_BIOPSY_SEQ_NUM = "T-15-000078"
NON_MATCHING_BIOPSY_SEQ_NUM = "T-15-nomatch"
# These will be returned from Patient._select_biopsy and an analysis ID will be found in Patient.get_analysis_id
MATCHING_GOOD_BIOPSY1 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, False, [CONFIRMED_NEXT_GEN_SEQ])
MATCHING_GOOD_BIOPSY2 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, False,
                                      [CONFIRMED_NEXT_GEN_SEQ, NOT_CONFIRMED_NEXT_GEN_SEQ])
MATCHING_GOOD_BIOPSY3 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, False,
                                      [NOT_CONFIRMED_NEXT_GEN_SEQ, CONFIRMED_NEXT_GEN_SEQ])
# These will not even be returned by Patient._select_biopsy
NOMATCH_GOOD_BIOPSY1 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, False, [CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_GOOD_BIOPSY2 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, False,
                                     [CONFIRMED_NEXT_GEN_SEQ, NOT_CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_GOOD_BIOPSY3 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, False,
                                     [NOT_CONFIRMED_NEXT_GEN_SEQ, CONFIRMED_NEXT_GEN_SEQ])
MATCHING_FAILED_BIOPSY1 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, True, [CONFIRMED_NEXT_GEN_SEQ])
MATCHING_FAILED_BIOPSY2 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, True,
                                        [CONFIRMED_NEXT_GEN_SEQ, NOT_CONFIRMED_NEXT_GEN_SEQ])
MATCHING_FAILED_BIOPSY3 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, True,
                                        [NOT_CONFIRMED_NEXT_GEN_SEQ, CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_FAILED_BIOPSY1 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, True, [CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_FAILED_BIOPSY2 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, True,
                                       [CONFIRMED_NEXT_GEN_SEQ, NOT_CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_FAILED_BIOPSY3 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, True,
                                       [NOT_CONFIRMED_NEXT_GEN_SEQ, CONFIRMED_NEXT_GEN_SEQ])
# These will be returned from Patient._select_biopsy, but no analysis ID will be found in Patient.get_analysis_id
MATCHING_BAD_BIOPSY1 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, False, [])
MATCHING_BAD_BIOPSY2 = create_biopsy(MATCHING_BIOPSY_SEQ_NUM, False, [NOT_CONFIRMED_NEXT_GEN_SEQ])
NOMATCH_BAD_BIOPSY1 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, False, [])
NOMATCH_BAD_BIOPSY2 = create_biopsy(NON_MATCHING_BIOPSY_SEQ_NUM, False, [NOT_CONFIRMED_NEXT_GEN_SEQ])

DEFAULT_ASSIGNMENT_IDX = 2
DEFAULT_PAT_ASSNMNT_STEP_NUM ="0"


def create_patient(triggers=None, assignment_logics=None, current_patient_status='ON_TREATMENT_ARM',
                   treatment_arm=None, biopsies=None, patient_assmnt_idx=DEFAULT_ASSIGNMENT_IDX,
                   patient_type="STANDARD", assignment_date=ASSIGNMENT_DATE, patient_sequence_number="14400",
                   pat_assignment_idx=0, current_step_number="0"):
    if triggers is None:
        triggers = DEFAULT_TRIGGERS
    if assignment_logics is None:
        assignment_logics = DEFAULT_ASSIGNMENT_LOGICS
    if biopsies is None:
        biopsies = []
    # NOTE:  No default value for treatment_arm because it is sometimes missing from Patient records.

    patient = {
        "patientSequenceNumber": patient_sequence_number,
        "patientType": patient_type,
        "patientTriggers": triggers,
        "biopsies": biopsies,
        "currentStepNumber": current_step_number,
        "currentPatientStatus": current_patient_status,
        "patientAssignmentIdx": pat_assignment_idx,
        "patientAssignments": {},  # is an array in the patient data model, but the query unwinds on that field
        "diseases": [
            {
                "ctepCategory": "Breast Neoplasm",
                "ctepSubCategory": "Breast Cancer - Invasive",
                "ctepTerm": "Invasive breast carcinoma",
                "shortName": "Invasive breast carcinoma"
            }
        ],
    }

    if len(assignment_logics):
        patient['patientAssignmentIdx'] = patient_assmnt_idx
        patient['patientAssignments'] = {
            "dateAssigned": datetime_to_timestamp(assignment_date),
            "biopsySequenceNumber": MATCHING_BIOPSY_SEQ_NUM,
            "patientAssignmentStatus": "AVAILABLE",
            "patientAssignmentLogic": assignment_logics,
            "patientAssignmentStatusMessage": "Patient registration to assigned treatment arm EAY131-B",
            "stepNumber": DEFAULT_PAT_ASSNMNT_STEP_NUM,
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
            "dateConfirmed": datetime_to_timestamp(datetime(2015, 9, 30, 12, 34, 55))
        }
    if treatment_arm is not None:
        if current_patient_status == 'ON_TREATMENT_ARM':
            patient['currentTreatmentArm'] = treatment_arm
        patient['patientAssignments']['treatmentArm'] = treatment_arm

    return patient


TEST_PATIENT_NO_TA = create_patient(current_patient_status='OFF_TRIAL', treatment_arm=None)
TEST_PATIENT = create_patient(DEFAULT_TRIGGERS, DEFAULT_ASSIGNMENT_LOGICS, 'ON_TREATMENT_ARM', PATIENT_TREATMENT_ARM)

NOT_ENROLLED_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, DECEASED_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-E"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    current_patient_status='OFF_TRIAL_DECEASED',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number="14441"
)
FORMER_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER, OFF_TRIAL_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-A"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    current_patient_status='OFF_TRIAL',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number = "14442"
)
PENDING_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-S"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-E"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    current_patient_status='PENDING_APPROVAL',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number = "14443"
)

# current_patient_status = 'ON_TREATMENT_ARM',
# treatment_arm = None, biopsies = None, patient_assmnt_idx = DEFAULT_ASSIGNMENT_IDX):

CURRENT_PATIENT = create_patient(
    triggers=[REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER],
    assignment_logics = [
        create_patient_assignment_logic("EAY131-H"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-G"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    current_patient_status='ON_TREATMENT_ARM',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number = "14444"
)
REGISTERED_PATIENT = create_patient(
    [
        REGISTRATION_TRIGGER,
    ],
    [],  # No assignments yet
    current_patient_status='REGISTERED',
    treatment_arm=None,
    patient_sequence_number = "14446"
)
REJOIN_DATE = PENDING_OFF_STUDY_DATE + timedelta(days=2)
NEW_PENDING_CONF_DATE = PENDING_OFF_STUDY_DATE + timedelta(days=3)
NEW_PENDING_CONF_TRIGGER = create_patient_trigger('PENDING_CONFIRMATION', date_created=NEW_PENDING_CONF_DATE)
REJOIN_TRIGGER = create_patient_trigger('REJOIN', date_created=REJOIN_DATE)
OFF_STUDY_REJOIN_PATIENT = create_patient(
    triggers=[REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER,
              REJOIN_TRIGGER, NEW_PENDING_CONF_TRIGGER,
              ],
    assignment_logics = [
        create_patient_assignment_logic("EAY131-U"),
        create_patient_assignment_logic("EAY131-G"),
        create_patient_assignment_logic("EAY131-E"),
    ],
    current_patient_status='PENDING_CONFIRMATION',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    assignment_date=NEW_PENDING_CONF_DATE,
    patient_sequence_number = "14447"
)

PENDING_CONF_APPR_CONF_PATIENT = create_patient(
    triggers=[REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER,
              # I don't think that in the real world a PENDING_CONFIRMATION trigger would follow a PENDING_APPROVAL
              # trigger, but it is a case that the code handles and therefore it must be tested.
              # UPDATE (1/13/2018):  No, this is not realistic at all.
              create_patient_trigger('PENDING_CONFIRMATION',
                                     date_created=PENDING_APPR_DATE + timedelta(minutes=2)),
              ],
    assignment_logics = [
        create_patient_assignment_logic("EAY131-C"),
        create_patient_assignment_logic("EAY131-G"),
        create_patient_assignment_logic("EAY131-A"),
        MATCHING_LOGIC,
    ],
    current_patient_status='PENDING_CONFIRMATION',
    assignment_date=PENDING_CONF_DATE,
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY2],
    patient_sequence_number = "14448"
)

PENDING_ON_PENDING_PATIENT = create_patient(
    triggers=[REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER,
              # I don't think that in the real world a PENDING_CONFIRMATION trigger would follow a ON_TREATMENT_ARM
              # trigger, but it is a case that the code handles and therefore it must be tested.
              # UPDATE (1/13/2018):  No, this is not realistic at all.  ON_TREATMENT_ARM would be followed by
              # PROGRESSION, OFF_TRIAL, or maybe a rebiopsy
              NEW_PENDING_CONF_TRIGGER,
              ],
    assignment_logics = [
        create_patient_assignment_logic("EAY131-A"),
        create_patient_assignment_logic("EAY131-G"),
        create_patient_assignment_logic("EAY131-U"),
        MATCHING_LOGIC,
    ],
    current_patient_status='PENDING_CONFIRMATION',
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    assignment_date=PENDING_CONF_DATE,
    patient_sequence_number = "14449"
)

NOT_ELIGIBLE_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, NOT_ELIGIBLE_TRIGGER, NEW_PENDING_CONF_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-E"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    'NOT_ELIGIBLE',
    PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number="14450"
)

COMPASSIONATE_CARE_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, COMPASSIONATE_CARE_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-E"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-U"),
        create_patient_assignment_logic("EAY131-G"),
    ],
    'COMPASSIONATE_CARE',
    PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY2],
    patient_sequence_number="14451"
)

PROGRESSION_REBIOPSY_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER, PROGRESSION_REBIOPSY_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-G"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-R"),
        create_patient_assignment_logic("EAY131-A"),
    ],
    'PROGRESSION_REBIOPSY',
    PATIENT_TREATMENT_ARM,
    current_step_number="2",
    biopsies=[MATCHING_GOOD_BIOPSY3],
    patient_sequence_number="14452"
)

DECEASED_PATIENT = create_patient(
    [REGISTRATION_TRIGGER, PENDING_CONF_TRIGGER, PENDING_APPR_TRIGGER, ON_ARM_TRIGGER, DECEASED_TRIGGER],
    [
        create_patient_assignment_logic("EAY131-Q"),
        MATCHING_LOGIC,
        create_patient_assignment_logic("EAY131-A"),
        create_patient_assignment_logic("EAY131-U"),
    ],
    current_patient_status='OFF_TRIAL_DECEASED',
    current_step_number="1",
    treatment_arm=PATIENT_TREATMENT_ARM,
    biopsies=[MATCHING_GOOD_BIOPSY1],
    patient_sequence_number = "14453"
)


# The data below is here to mimic an usual situation found in testing where a patient was assigned to the
# same arm twice.  It resulted in the patient erroneously being counted twice in the summary report refresh.
# This data reflects the fact that the way the data is returned from the database, everything will be the
# same except for the assignment records and patientAssignmentIdx.
# UPDATE (1/13/2018):  This must've been bad data in the test database because the matching rules will always exclude
# previously assigned arms.  Therefore, a patient will never be assigned the same arm twice.
PATIENT_TWICE_SEQ_NUM = "10385"
PATIENT_TWICE_TRTMT_ARM_ID = "EAY131-U"
PATIENT_TWICE_TREATMENT_ARM = {
    "_id": PATIENT_TWICE_TRTMT_ARM_ID,  # NOTE: This ID is in the treatmentId field in the treatmentArms collection.
    "name": "VS-6063( defactinib) in tumor with NF2 loss",
    "version": "2016-01-20",
    "numPatientsAssigned": 2,
    "maxPatientsAllowed": 35,
    "treatmentArmStatus": "OPEN",
}

PATIENT_TWICE_TRIGGERS = [
    create_patient_trigger('REGISTRATION', date_created=datetime(2015, 9, 28, 19, 1, 38),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_CONFIRMATION', date_created=datetime(2015, 12, 1, 14, 46, 13),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_APPROVAL', date_created=datetime(2015, 12, 1, 17, 36, 13),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('NOT_ELIGIBLE', date_created=datetime(2015, 12, 16, 14, 23, 13),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_CONFIRMATION', date_created=datetime(2015, 12, 16, 14, 23, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_OFF_STUDY', date_created=datetime(2015, 12, 16, 14, 26, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('OFF_TRIAL_NO_TA_AVAILABLE', date_created=datetime(2015, 12, 16, 14, 28, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('REJOIN_REQUESTED', date_created=datetime(2016, 2, 25, 18, 27, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('REJOIN', date_created=datetime(2016, 2, 26, 16, 39, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_CONFIRMATION', date_created=datetime(2016, 2, 26, 16, 39, 55),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_APPROVAL', date_created=datetime(2016, 2, 26, 19, 9, 55),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('NOT_ELIGIBLE', date_created=datetime(2016, 3, 18, 15, 17, 55),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_CONFIRMATION', date_created=datetime(2016, 3, 18, 15, 14, 23, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('PENDING_OFF_STUDY', date_created=datetime(2016, 3, 18, 15, 26, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
    create_patient_trigger('OFF_TRIAL_NO_TA_AVAILABLE', date_created=datetime(2016, 3, 18, 15, 28, 21),
                           patient_seq_num=PATIENT_TWICE_SEQ_NUM),
]
PATIENT_TWICE_MATCHING_LOGIC = \
    create_patient_assignment_logic(PATIENT_TWICE_TRTMT_ARM_ID,
                                    reason="The patient and treatment arm match on non-hotspot variant.",
                                    category="SELECTED")

PATIENT_ON_ARM_TWICE1 = create_patient(
    pat_assignment_idx=0,
    patient_sequence_number=PATIENT_TWICE_SEQ_NUM,
    treatment_arm=PATIENT_TWICE_TREATMENT_ARM,
    triggers=PATIENT_TWICE_TRIGGERS,
    assignment_date=datetime(2015, 12, 1, 14, 46, 13),
    assignment_logics=[PATIENT_TWICE_MATCHING_LOGIC],
    current_patient_status="OFF_TRIAL_NO_TA_AVAILABLE"
)
PATIENT_ON_ARM_TWICE2 = create_patient(
    pat_assignment_idx=2,
    patient_sequence_number=PATIENT_TWICE_SEQ_NUM,
    treatment_arm=PATIENT_TWICE_TREATMENT_ARM,
    triggers=PATIENT_TWICE_TRIGGERS,
    assignment_date=datetime(2016, 2, 26, 16, 39, 55),
    assignment_logics=[PATIENT_TWICE_MATCHING_LOGIC],
    current_patient_status="OFF_TRIAL_NO_TA_AVAILABLE"
)
