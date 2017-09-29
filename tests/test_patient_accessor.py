#!/usr/bin/env python3

import unittest
from mock import patch, Mock
from ddt import ddt, data, unpack

from accessors.patient_accessor import PatientAccessor


TEST_PATIENT_API_URL = "http://my/test/patient_api"


@ddt
class PatientAccessorTests(unittest.TestCase):
    def setUp(self):
        env_patcher = patch('accessors.patient_accessor.Environment')
        self.addCleanup(env_patcher.stop)
        self.mock_env = env_patcher.start().return_value
        self.mock_env.patient_api_url = TEST_PATIENT_API_URL

        logging_patcher = patch('accessors.patient_accessor.logging')
        self.addCleanup(logging_patcher.stop)
        self.mock_logger = logging_patcher.start().getLogger()

    def test_constructor(self):
        self.assertEqual(PatientAccessor().url, TEST_PATIENT_API_URL+'/by_treatment_arm')

    @data(
        (None, {}),
        ("Bearer ThisIsMyFakeAuth0TokenId", {"authorization": "Bearer ThisIsMyFakeAuth0TokenId"})
    )
    @unpack
    @patch('accessors.patient_accessor.requests')
    def test_get_patients_by_treatment_arm_id(self, authorization_token, exp_headers, mock_requests):
        # Doesn't really matter what the treatment arm ID is or what patients are returned; just verifying here that
        # the service is called correctly and the returned data is handled correctly.
        treatment_id = "TA_ID_5"
        patients = [{'patientSequenceNumber': 1}, {'patientSequenceNumber': 2}, {'patientSequenceNumber': 3}]

        mock_response = Mock()
        mock_response.json.return_value = patients
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response

        patient_accessor = PatientAccessor()
        result = patient_accessor.get_patients_by_treatment_arm_id(treatment_id, authorization_token)

        exp_url = TEST_PATIENT_API_URL + '/by_treatment_arm/' + treatment_id
        mock_requests.get.assert_called_once_with(exp_url, headers=exp_headers)
        mock_response.json.assert_called_once_with()
        self.assertEqual(result, patients)

    @data(
        (401, {'code': 'invalid_token', 'description': 'token is invalid'},
         TEST_PATIENT_API_URL + "/by_treatment_arm returned 401: token is invalid"),
        (500, {'error_msg_in_other_format': 'description of the error'},
         TEST_PATIENT_API_URL + "/by_treatment_arm returned 500: " +
         str({'error_msg_in_other_format': 'description of the error'})),
    )
    @unpack
    @patch('accessors.patient_accessor.requests')
    def test_get_patients_by_treatment_arm_id_with_exc(self, status_code, response_data, exp_exc_msg, mock_requests):
        # Doesn't really matter what the treatment arm ID is; just verifying here that the service
        # is called correctly and the returned data is formatted correctly in an exception.
        treatment_id = "TA_ID_5"

        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.status_code = status_code
        mock_requests.get.return_value = mock_response

        patient_accessor = PatientAccessor()
        with self.assertRaises(Exception) as cm:
            patient_accessor.get_patients_by_treatment_arm_id(treatment_id, {})

        exp_url = TEST_PATIENT_API_URL + '/by_treatment_arm/' + treatment_id
        mock_requests.get.assert_called_once_with(exp_url, headers={})
        mock_response.json.assert_called_once_with()
        self.assertEqual(str(cm.exception), exp_exc_msg)


if __name__ == '__main__':
    unittest.main()
