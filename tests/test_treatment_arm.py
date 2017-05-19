import datetime
import re
import unittest

import flask
from ddt import ddt, data, unpack
from mock import patch

from resources import treatment_arm


def is_active_only_request(req_context):
    return True if re.search('active=(true|1)(\b|$|&)', req_context, re.IGNORECASE) else False


def filter_out_inactives(ta_list):
    return [ta for ta in ta_list if ta['dateArchived'] is None]


ACTIVE_ARMS = [
    {
        "_id": {
            "$oid": "59146fa28055228d2404b48f"
        },
        "dateArchived": None,
        "name": "MLN0128(TAK-228) in TSC 1 and TSC2 mutations",
        "stateToken": {
            "$uuid": "2189eea04b434ff289c485fade756616"
        },
        "treatmentArmDrugs": [
            {
                "drugId": "768435",
                "name": "MLN0128(TAK-228)",
                "pathway": "PI3K/AKT/mTOR"
            }
        ],
        "treatmentId": "EAY131-M",
        "version": "2017-03-13"
    },
    {
        "_id": {
            "$oid": "59146fa28055228d2404b48e"
        },
        "dateArchived": None,
        "name": "MLN0128(TAK-228) in mTOR mutations",
        "stateToken": {
            "$uuid": "b3c772a0005d4e6e811ccfbddfbe87eb"
        },
        "treatmentArmDrugs": [
            {
                "drugId": "768435",
                "name": "MLN0128(TAK-228)",
                "pathway": "mTOR"
            }
        ],
        "treatmentId": "EAY131-L",
        "version": "2017-03-12"
    },
]

ARCHIVED_ARMS = [
    {
        "_id": {
            "$oid": "59146fa28055228d2404b4bf"
        },
        "dateArchived": datetime.datetime(2016, 1, 13, 21, 8, 22, 83000),
        "name": "MLN0128(TAK-228) in mTOR mutations",
        "stateToken": {
            "$uuid": "a52477883d4d485a9e6f45c8f27f74eb"
        },
        "treatmentArmDrugs": [
            {
                "drugId": "768435",
                "name": "MLN0128(TAK-228)",
                "pathway": "mTOR"
            }
        ],
        "treatmentId": "EAY131-L",
        "version": "2017-03-11"
    },
    {
        "_id": {
            "$oid": "59146fa28055228d2404b4c0"
        },
        "dateArchived": datetime.datetime(2016, 1, 15, 21, 36, 20, 602000),
        "name": "MLN0128(TAK-228) in TSC 1 and TSC2 mutations",
        "stateToken": {
            "$uuid": "e890a857e5b34d63ba0909fd78a07215"
        },
        "treatmentArmDrugs": [
            {
                "drugId": "768435",
                "name": "MLN0128(TAK-228)",
                "pathway": "PI3K/AKT/mTOR"
            }
        ],
        "treatmentId": "EAY131-M",
        "version": "2017-03-11"
    },
    {
        "_id": {
            "$oid": "59146fa28055228d2404b4c1"
        },
        "dateArchived": datetime.datetime(2016, 6, 6, 14, 56, 52, 704000),
        "name": "MLN0128(TAK-228) in TSC 1 and TSC2 mutations",
        "stateToken": {
            "$uuid": "d2ff75453f1f475abf35efc638cae055"
        },
        "treatmentArmDrugs": [
            {
                "drugId": "768435",
                "name": "MLN0128(TAK-228)",
                "pathway": "PI3K/AKT/mTOR"
            }
        ],
        "treatmentId": "EAY131-M",
        "version": "2017-03-12"
    }
]

ALL_ARMS = ACTIVE_ARMS + ARCHIVED_ARMS

NO_ARMS = []


@ddt
class TestTreatmentArms(unittest.TestCase):

    # QUERIES - for checking that the correct query is passed to TreatmentArmsAccessor.find()
    DEFAULT_QUERY = {}
    ACTIVE_QRY = {'dateArchived': {"$eq": None}}

    # PROJECTIONS - for checking that the correct projection is passed to TreatmentArmsAccessor.find()
    DEFAULT_PROJECTION = None
    ID_PROJECTION = {'_id': 1}
    NAME_PROJECTION = {'name': 1, '_id': 0}
    NAME_AND_ID_PROJECTION = {'name': 1, '_id': 1}

    @data(
        (100, ALL_ARMS,  '', ALL_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (101, ALL_ARMS, '?active=101', ALL_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (102, ALL_ARMS, '?active=True', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (103, ALL_ARMS, '?active=TRUE', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (104, ALL_ARMS, '?active=1', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),

        (200, ACTIVE_ARMS, '', ACTIVE_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (201, ACTIVE_ARMS, '?active=False', ACTIVE_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (202, ACTIVE_ARMS, '?active=True', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (203, ACTIVE_ARMS, '?active=TRUE', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (204, ACTIVE_ARMS, '?active=1', ACTIVE_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),

        (300, ARCHIVED_ARMS, '', ARCHIVED_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (301, ARCHIVED_ARMS, '?active=Bogus', ARCHIVED_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (302, ARCHIVED_ARMS, '?active=True', NO_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (303, ARCHIVED_ARMS, '?active=TRUE', NO_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),
        (304, ARCHIVED_ARMS, '?active=1', NO_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),

        (400, NO_ARMS, '?active=False', NO_ARMS, DEFAULT_QUERY, DEFAULT_PROJECTION),
        (401, NO_ARMS, '?active=1', NO_ARMS, ACTIVE_QRY, DEFAULT_PROJECTION),

        # Test for projection; this is done exclusively by checking that the projection parameter passed to the
        # mocked TreatmentArmAccessor object is what is expected.  MongoDb does the actual filtering, so there
        # is nothing to test in that regard.
        (500, ALL_ARMS, '?projection=name', ALL_ARMS, DEFAULT_QUERY, NAME_PROJECTION),
        (501, ALL_ARMS, '?active=1&projection=_id,name', ACTIVE_ARMS, ACTIVE_QRY, NAME_AND_ID_PROJECTION),
        (502, ALL_ARMS, '?projection=name,_id&active=True', ACTIVE_ARMS, ACTIVE_QRY, NAME_AND_ID_PROJECTION),
        (503, ALL_ARMS, '?active=TRUE&projection=_id', ACTIVE_ARMS, ACTIVE_QRY, ID_PROJECTION),
    )
    @unpack
    @patch('resources.treatment_arm.TreatmentArmsAccessor')
    def test_get(self, test_id, test_data, request_context, exp_result, exp_qry_param, exp_proj_param,
                 mock_ta_accessor):
        active_only = is_active_only_request(request_context)
        instance = mock_ta_accessor.return_value
        instance.find.return_value = test_data if not active_only else filter_out_inactives(test_data)

        app = flask.Flask(__name__)
        with app.test_request_context(request_context):
            result = treatment_arm.TreatmentArms.get()
            self.assertEqual(result, exp_result, "TestTreatmentArms Test Case %d" % test_id)
            instance.find.assert_called_with(exp_qry_param, exp_proj_param)


@ddt
class TestTreatmentArmsById(unittest.TestCase):
    # TEST DATA
    EAY131M_ACTIVE_ARMS = [arm for arm in ACTIVE_ARMS if arm['treatmentId'] == 'EAY131-M']
    EAY131M_ARCHIVED_ARMS = [arm for arm in ARCHIVED_ARMS if arm['treatmentId'] == 'EAY131-M']
    EAY131M_ALL_ARMS = EAY131M_ACTIVE_ARMS + EAY131M_ARCHIVED_ARMS

    EAY131L_ACTIVE_ARMS = [arm for arm in ACTIVE_ARMS if arm['treatmentId'] == 'EAY131-L']
    EAY131L_ARCHIVED_ARMS = [arm for arm in ARCHIVED_ARMS if arm['treatmentId'] == 'EAY131-L']
    EAY131L_ALL_ARMS = EAY131L_ACTIVE_ARMS + EAY131L_ARCHIVED_ARMS

    # QUERIES - for checking that the correct query is passed to TreatmentArmsAccessor.find()
    EAY131M_ALL_QRY = {"treatmentId": 'EAY131-M'}
    EAY131M_ACTIVE_QRY = {"treatmentId": 'EAY131-M', 'dateArchived': {"$eq": None}}
    EAY131L_ALL_QRY = {"treatmentId": 'EAY131-L'}
    EAY131L_ACTIVE_QRY = {"treatmentId": 'EAY131-L', 'dateArchived': {"$eq": None}}
    NO_EXIST_ALL_QRY = {"treatmentId": 'NO_EXIST'}
    NO_EXIST_ACTIVE_QRY = {"treatmentId": 'NO_EXIST', 'dateArchived': {"$eq": None}}

    # PROJECTIONS - for checking that the correct projection is passed to TreatmentArmsAccessor.find()
    DEFAULT_PROJECTION = None
    ID_PROJECTION = {'_id': 1}
    NAME_PROJECTION = {'name': 1, '_id': 0}
    NAME_AND_ID_PROJECTION = {'name': 1, '_id': 1}

    @data(
        (100, 'EAY131-M', ALL_ARMS, '', EAY131M_ALL_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (101, 'EAY131-M', ACTIVE_ARMS, '', EAY131M_ACTIVE_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (102, 'EAY131-M', ARCHIVED_ARMS, '', EAY131M_ARCHIVED_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (103, 'EAY131-M', NO_ARMS, '', NO_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (104, 'EAY131-M', EAY131M_ACTIVE_ARMS, '', EAY131M_ACTIVE_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (105, 'EAY131-M', EAY131M_ARCHIVED_ARMS, '', EAY131M_ARCHIVED_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (106, 'EAY131-M', EAY131M_ALL_ARMS, '', EAY131M_ALL_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),
        (107, 'EAY131-M', EAY131L_ACTIVE_ARMS, '', NO_ARMS, EAY131M_ALL_QRY, DEFAULT_PROJECTION),

        (200, 'EAY131-L', ALL_ARMS, '', EAY131L_ALL_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (201, 'EAY131-L', ACTIVE_ARMS, '', EAY131L_ACTIVE_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (202, 'EAY131-L', ARCHIVED_ARMS, '', EAY131L_ARCHIVED_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (203, 'EAY131-L', NO_ARMS, '', NO_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (204, 'EAY131-L', EAY131L_ACTIVE_ARMS, '', EAY131L_ACTIVE_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (205, 'EAY131-L', EAY131L_ARCHIVED_ARMS, '', EAY131L_ARCHIVED_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (206, 'EAY131-L', EAY131L_ALL_ARMS, '', EAY131L_ALL_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),
        (207, 'EAY131-L', EAY131M_ACTIVE_ARMS, '', NO_ARMS, EAY131L_ALL_QRY, DEFAULT_PROJECTION),

        (300, 'EAY131-M', ALL_ARMS, '?active=1', EAY131M_ACTIVE_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (301, 'EAY131-M', ACTIVE_ARMS, '?active=1', EAY131M_ACTIVE_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (302, 'EAY131-M', ARCHIVED_ARMS, '?active=1', NO_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (303, 'EAY131-M', NO_ARMS, '?active=1', NO_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (304, 'EAY131-M', EAY131M_ACTIVE_ARMS, '?active=1', EAY131M_ACTIVE_ARMS, EAY131M_ACTIVE_QRY,
            DEFAULT_PROJECTION),
        (305, 'EAY131-M', EAY131M_ARCHIVED_ARMS, '?active=1', NO_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (306, 'EAY131-M', EAY131M_ALL_ARMS, '?active=1', EAY131M_ACTIVE_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),
        (307, 'EAY131-M', EAY131L_ACTIVE_ARMS, '?active=1', NO_ARMS, EAY131M_ACTIVE_QRY, DEFAULT_PROJECTION),

        (400, 'EAY131-L', ALL_ARMS, '?active=1', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (401, 'EAY131-L', ACTIVE_ARMS, '?active=1', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (402, 'EAY131-L', ARCHIVED_ARMS, '?active=1', NO_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (403, 'EAY131-L', NO_ARMS, '?active=1', NO_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (404, 'EAY131-L', EAY131L_ACTIVE_ARMS, '?active=1', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY,
            DEFAULT_PROJECTION),
        (405, 'EAY131-L', EAY131L_ARCHIVED_ARMS, '?active=1', NO_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (406, 'EAY131-L', EAY131L_ALL_ARMS, '?active=1', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),
        (407, 'EAY131-L', EAY131M_ACTIVE_ARMS, '?active=1', NO_ARMS, EAY131L_ACTIVE_QRY, DEFAULT_PROJECTION),

        (500, 'NO_EXIST', ALL_ARMS, '', NO_ARMS, NO_EXIST_ALL_QRY, DEFAULT_PROJECTION),
        (501, 'NO_EXIST', ALL_ARMS, '?active=1', NO_ARMS, NO_EXIST_ACTIVE_QRY, DEFAULT_PROJECTION),

        # Test for projection; this is done exclusively by checking that the projection parameter passed to the
        # mocked TreatmentArmAccessor object is what is expected.  MongoDb does the actual filtering, so there
        # is nothing to test in that regard.
        (600, 'EAY131-L', ALL_ARMS, '?active=1&projection=name', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY,
            NAME_PROJECTION),
        (601, 'EAY131-L', ALL_ARMS, '?active=1&projection=name,_id', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY,
            NAME_AND_ID_PROJECTION),
        (602, 'EAY131-L', ALL_ARMS, '?active=1&projection=_id,name', EAY131L_ACTIVE_ARMS, EAY131L_ACTIVE_QRY,
            NAME_AND_ID_PROJECTION),
        (603, 'EAY131-L', ALL_ARMS, '?projection=_id', EAY131L_ALL_ARMS, EAY131L_ALL_QRY, ID_PROJECTION),
    )
    @unpack
    @patch('resources.treatment_arm.TreatmentArmsAccessor')
    def test_get(self, test_id, arm_id, test_data, request_context, exp_result, exp_qry_param,
                 exp_proj_param, mock_ta_accessor):
        self.maxDiff = None
        active_only = is_active_only_request(request_context)
        instance = mock_ta_accessor.return_value
        instance.find.return_value = TestTreatmentArmsById._create_find_return(test_data, arm_id, active_only)

        app = flask.Flask(__name__)
        with app.test_request_context(request_context):
            result = treatment_arm.TreatmentArmsById.get(arm_id)
            instance.find.assert_called_with(exp_qry_param, exp_proj_param)
            self.assertEqual(len(result), len(exp_result), "TestTreatmentArmsById Test Case %d" % test_id)
            self.assertEqual(TestTreatmentArmsById._sort(result), TestTreatmentArmsById._sort(exp_result),
                             "TestTreatmentArmsById Test Case %d" % test_id)

    @staticmethod
    def _sort(result):
        # sort_field = 'dateArchived'
        # return sorted(result, key=lambda r: r[sort_field] if r[sort_field] is not None else datetime.datetime.now())
        return sorted(result, key=lambda r: str(r))

    @staticmethod
    def _create_find_return(test_data, arm_id, active_only):
        requested_arms = [arm for arm in test_data if arm['treatmentId'] == arm_id]
        if active_only:
            requested_arms = filter_out_inactives(requested_arms)
        return requested_arms

if __name__ == '__main__':
    unittest.main()
