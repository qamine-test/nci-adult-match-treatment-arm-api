

class SummaryReport:
    # Patient Type Constants
    NOT_ENROLLED = 'numNotEnrolledPatients'
    FORMER = 'numFormerPatients'
    PENDING = 'numPendingArmApproval'
    CURRENT = 'numCurrentPatientsOnArm'

    _SR_COUNT_FIELDS = [NOT_ENROLLED, FORMER, CURRENT, PENDING]
    _REQ_JSON_FIELDS = ['_id', 'treatmentId', 'version', 'treatmentArmStatus', 'summaryReport']
    _REQ_SR_FIELDS = _SR_COUNT_FIELDS + ['assignmentRecords']

    @staticmethod
    def _validate_sr_json_doc(sr_json_doc):
        if sr_json_doc is None:
            sr_json_doc = dict()
        missing_fields = [f for f in SummaryReport._REQ_JSON_FIELDS if f not in sr_json_doc]
        sr = sr_json_doc['summaryReport'] if 'summaryReport' in sr_json_doc else dict()
        missing_fields += ['summaryReport.'+f for f in SummaryReport._REQ_SR_FIELDS if f not in sr]

        if missing_fields:
            err_msg = ("The following required fields were missing from the submitted summary report JSON document: "
                       + ", ".join(missing_fields))
            raise Exception(err_msg)

    def __init__(self, sr_json_doc):
        """

        :param sr_json_doc:
        """
        SummaryReport._validate_sr_json_doc(sr_json_doc)
        self.sr = sr_json_doc

    def __getattr__(self, item):
        if item in SummaryReport._REQ_SR_FIELDS:
            return self.sr['summaryReport'][item]
        else:
            return self.sr[item]

    def add_patient_by_type(self, pat_type):
        """

        :param pat_type: patient type (must be one of the patient type constants defined above)
        :return:
        """
        if pat_type not in SummaryReport._SR_COUNT_FIELDS:
            raise Exception("Invalid patient type '{t}'".format(t=pat_type))
        self.sr['summaryReport'][pat_type] += 1

