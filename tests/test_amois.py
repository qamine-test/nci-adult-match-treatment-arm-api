import unittest
import datetime
# import flask
from ddt import ddt, data, unpack
# from mock import patch
from resources import amois


# def create_vr_dict(e, f, g, o):
#     return { 'exon': e, 'function': f, 'oncominevariantclass': o, 'gene': g}
#
# def create_nhr_dict(e, f, g, o):
#     nhr = dict()
#     if e:
#         nhr['exon'] = e
#     if f:
#         nhr['function'] = f
#     if g:
#         nhr['exon'] = g
#     if o:
#         nhr['oncominevariantclass'] = o
#     if not nhr:
#         raise Exception("bad test data: NonHotspotRule requires at least one field.")
#     return nhr


@ddt
class TestStateAssignment(unittest.TestCase):
    @data(
        ({'treatmentArmStatus': 'PENDING', 'dateArchived': None}, 'FUTURE'),
        ({'treatmentArmStatus': 'READY', 'dateArchived': None}, 'FUTURE'),
        ({'treatmentArmStatus': 'OPEN', 'dateArchived': None}, 'CURRENT'),
        ({'treatmentArmStatus': 'CLOSED', 'dateArchived': None}, 'PRIOR'),
        ({'treatmentArmStatus': 'SUSPENDED', 'dateArchived': None}, 'PRIOR'),
        ({'treatmentArmStatus': 'PENDING', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'READY', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'OPEN', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'CLOSED', 'dateArchived': 'not None'}, 'PREVIOUS'),
        ({'treatmentArmStatus': 'SUSPENDED', 'dateArchived': datetime.datetime.now()}, 'PREVIOUS'),
    )
    @unpack
    def test_get_amoi_state(self, ta_nhr, exp_state):
        state = amois.get_amoi_state(ta_nhr)
        self.assertEqual(state, exp_state)

    @data(
        ({'treatmentArmStatus': 'PENDI', 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'PENDI' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': '', 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status '' for TreatmentArm 'EAY-1', version 2016-09-09"),
        ({'treatmentArmStatus': None, 'dateArchived': None, 'treatmentId': 'EAY-1', 'version': '2016-09-09'},
         "Unknown status 'None' for TreatmentArm 'EAY-1', version 2016-09-09"),
    )
    @unpack
    def test_get_amoi_state_with_exc(self, ta_nhr, exp_exp_msg):
        with self.assertRaises(Exception) as cm:
            amois.get_amoi_state(ta_nhr)
        self.assertEqual(str(cm.exception), exp_exp_msg)


@ddt
class TestAmoisAnnotator(unittest.TestCase):
    def test_get(self):
        pass


if __name__ == '__main__':
    unittest.main()
