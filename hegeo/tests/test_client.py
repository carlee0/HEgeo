import unittest
import numpy as np
import seal
from seal import EncryptionParameters, scheme_type, CoeffModulus
from ..client import Client


class ClientTest(unittest.TestCase):
    client = Client()

    def test_client(self):
        self.assertIsInstance(Client(), type(self.client))

    def test_parms(self):
        # test set_parms_from_dict
        parms_dict = {"poly": 4096, "coeff": 2048, "plain": (1 << 8)}
        self.client.set_parms_from_dict(**parms_dict)
        self.assertIsInstance(Client(), type(self.client))
        self.assertEqual(self.client.get_parms().poly_modulus_degree(), parms_dict['poly'])
        self.assertEqual(self.client.get_parms().plain_modulus().value(), parms_dict['plain'])

        # test set_params
        parms = EncryptionParameters(scheme_type.BFV)
        poly_modulus_degree = 8192
        parms.set_poly_modulus_degree(poly_modulus_degree)
        parms.set_coeff_modulus(CoeffModulus.BFVDefault(poly_modulus_degree))
        parms.set_plain_modulus(256)
        self.client.set_parms(parms)
        self.assertIsInstance(Client(), type(self.client))
        self.assertEqual(self.client.get_parms().poly_modulus_degree(), poly_modulus_degree)
        self.assertEqual(self.client.get_parms().plain_modulus().value(), 256)
        self.assertIsInstance(self.client.public_key, seal.PublicKey)
        self.assertIsInstance(self.client.secret_key, seal.SecretKey)
        print(self.client.public_key)

    def test_enc_dec(self):
        print(self.client.public_key)
        arr = np.array([3, 1, 0, -2, -4])
        arr_c = self.client.enc(arr)
        arr_p = self.client.dec(arr_c)
        self.assertTrue(np.array_equal(arr_p, arr))

    def test_masking(self):
        arr = np.array([3, 1, 0, -2, -4])
        arr_masked = np.array([1, 1, 0, -1, -1])
        self.assertTrue(np.array_equal(self.client.masking(arr), arr_masked))
