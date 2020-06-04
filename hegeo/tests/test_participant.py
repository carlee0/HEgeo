import unittest
from ..participant import Participant
from ..client import Client
import numpy as np
from seal import EncryptionParameters, scheme_type, CoeffModulus, SEALContext, IntegerEncoder, Evaluator


class ParticipantTest(unittest.TestCase):

    participant = Participant()
    parms = EncryptionParameters(scheme_type.BFV)
    parms.set_poly_modulus_degree(4096)
    parms.set_coeff_modulus(CoeffModulus.BFVDefault(4096))
    parms.set_plain_modulus(1 << 8)

    def test_set_parms(self):
        self.participant._set_parms(self.parms)
        self.assertIsInstance(Participant(), type(self.participant))
        self.assertEqual(self.participant._parms.poly_modulus_degree(), 4096)
        self.assertEqual(self.participant._parms.plain_modulus().value(), 1 << 8)

        self.assertIsInstance(self.participant._context, SEALContext)
        self.assertIsInstance(self.participant._encoder, IntegerEncoder)
        self.assertIsInstance(self.participant._evaluator, Evaluator)

    def test_save_load_c_array(self):
        client = Client()
        arr = np.array([3, 1, 0, -2, -4])
        self.participant._set_parms(self.parms)
        arr_cipher = client.enc(arr)
        arr_string = self.participant.save_c_arr(arr_cipher)
        print(arr_string)
        arr_cipher_load = self.participant.load_c_arr(arr_string)
        arr_load = client.dec(arr_cipher_load)
        self.assertTrue(np.array_equal(arr, arr_load))







