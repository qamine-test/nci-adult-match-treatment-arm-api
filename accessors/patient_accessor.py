"""
Patient Accessor
"""

import logging

import requests

from helpers.environment import Environment
# from oauthlib.oauth2 import LegacyApplicationClient
# from requests_oauthlib import OAuth2Session
# from threading import Lock

class PatientAccessor(object):
    """
    The Patient data accessor
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.url = "{}/{}".format(Environment().patient_api_url, 'by_treatment_arm')
        # self.lock = Lock()
        # self.client = LegacyApplicationClient(client_id='')
        # self.oauth = OAuth2Session(client=self.client)
        # self.token = self.oauth.fetch_token(token_url="https://ncimatch.auth0.com/oauth/ro",
        #                                     client_id='',
        #                                     client_secret='',
        #                                     username='matchbox-test@mail.nih.gov', password='',
        #                                     connection='Adult-MATCH-IntTest')
        # self.scope = "openid roles email".split(' ')

    def get_patients_by_treatment_arm_id(self, trtmt_id, authorization_token=None):
        """
        Gets patient data for patients associated (currently or formerly) with the given TreatmentId.
        The patients will be sorted by patientSequenceNumber (ascending) and patientAssignments.dateConfirmed
        (descending).
        :param trtmt_id: a string containing the TreatmentArm ID
        :return: array of JSON documents containing required fields for Summary Report Refresh analysis
        """
        trtmt_id_url = "{}/{}".format(self.url, trtmt_id)
        headers = {"Authorization": authorization_token} if authorization_token else {}

        self.logger.debug('Retrieving Patients from {}'.format(trtmt_id_url))
        # self.logger.debug('Token: {}'.format(str(self.token)))
        self.logger.debug('Token: {}'.format(headers.get('Authorization', None)))
        # self.lock.acquire()
        try:
            # oauth = OAuth2Session(client=self.client, token=self.token, scope=self.scope)
            #
            # response = oauth.get(trtmt_id_url)
            response = requests.get(trtmt_id_url, headers=headers)

        except Exception as e:
            err_msg = "GET {url} resulted in exception: {exc}".format(url=self.url, exc=str(e))
            raise Exception(err_msg)
        # finally:
        #     self.lock.release()

        result = response.json()

        self.logger.debug('status_code: {}'.format(response.status_code))
        if response.status_code != 200:
            desc = result['description'] if 'description' in result else str(result)
            err_msg = "{url} returned {code}: {description}".format(url=self.url, code=response.status_code,
                                                                    description=desc)
            raise Exception(err_msg)

        return result

    # class PatientAccessor(MongoDbAccessor):
    #     """
    #     The Patient data accessor
    #     """
    #     # def __init__(self):
    #     MongoDbAccessor.__init__(self, 'patient', logging.getLogger(__name__))
    #
    # def get_patients_by_treatment_arm_id(self, trtmt_id):
    #     """
    #     Gets patient data for patients associated (currently or formerly) with the given TreatmentId.
    #     The patients will be sorted by patientSequenceNumber (ascending) and patientAssignments.dateConfirmed
    #     (descending).
    #     :param trtmt_id: a string containing the TreatmentArm ID
    #     :return: array of JSON documents containing required fields for Summary Report Refresh analysis
    #     """
    #     self.logger.debug('Retrieving Patient documents for Summary Report Refresh analysis')
    #     return [pat for pat in
    #             self.aggregate([{"$unwind": {"path": "$patientAssignments",
    #                                          "includeArrayIndex": "patientAssignmentIdx"}},
    #                             {"$match": {"patientAssignments.treatmentArm.treatmentArmId": trtmt_id}},
    #                             {"$project": {"currentPatientStatus": 1,
    #                                           "patientAssignmentIdx": 1,
    #                                           "patientAssignments": 1,
    #                                           "patientSequenceNumber": 1,
    #                                           "currentStepNumber": 1,
    #                                           "patientTriggers": 1,
    #                                           "diseases": 1,
    #                                           "biopsies": 1,
    #                                           "treatmentArm": "$patientAssignments.treatmentArm"}},
    #                             {"$sort": {"patientSequenceNumber": 1, "patientAssignments.dateAssigned": -1}},
    #                             ])]
