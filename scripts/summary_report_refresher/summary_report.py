

class SummaryReport:
    # Patient Type Constants
    NOT_ENROLLED = 'numNotEnrolledPatient'
    FORMER = 'numFormerPatients'
    PENDING = 'numPendingArmApproval'
    CURRENT = 'numCurrentPatientsOnArm'
    ASSNMNT_RECS = 'assignmentRecords'

    _SR_COUNT_FIELDS = [NOT_ENROLLED, FORMER, CURRENT, PENDING]
    _REQ_JSON_FIELDS = ['_id', 'treatmentId', 'version', 'treatmentArmStatus']
    _REQ_SR_FIELDS = _SR_COUNT_FIELDS + ['assignmentRecords']

    @staticmethod
    def _validate_sr_json_doc(ta_json_doc):
        if ta_json_doc is None:
            ta_json_doc = dict()
        missing_fields = [f for f in SummaryReport._REQ_JSON_FIELDS if f not in ta_json_doc]
        # sr = ta_json_doc['summaryReport'] if 'summaryReport' in ta_json_doc else dict()
        # missing_fields += ['summaryReport.'+f for f in SummaryReport._REQ_SR_FIELDS if f not in sr]

        if missing_fields:
            err_msg = ("The following required fields were missing from the submitted summary report JSON document: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)

    def __init__(self, ta_json_doc):
        """

        :param ta_json_doc:
        """
        SummaryReport._validate_sr_json_doc(ta_json_doc)
        self.ta = ta_json_doc
        self.sr = dict([(f, 0) for f in SummaryReport._SR_COUNT_FIELDS])
        self.sr[SummaryReport.ASSNMNT_RECS] = []

    def __getattr__(self, item):
        if item in SummaryReport._REQ_SR_FIELDS:
            return self.sr[item]
        else:
            return self.ta[item]

    def add_patient_by_type(self, pat_type):
        """

        :param pat_type: patient type (must be one of the patient type constants defined above)
        :return:
        """
        if pat_type not in SummaryReport._SR_COUNT_FIELDS:
            raise Exception("Invalid patient type '{t}'".format(t=pat_type))
        self.sr[pat_type] += 1

    def get_json(self):
        """
        Returns the structure needed to update the database.
        :return: a dict containing the full summary report structure
        """
        return self.sr
