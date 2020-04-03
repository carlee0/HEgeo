import unittest
import numpy as np
from ..client import Client


class ClientTest(unittest.TestCase):
    client = Client()

    def test_client(self):
        self.assertIsInstance(Client(), type(self.client))

        parms_dict = {"poly": 4096, "coeff": 2048, "plain": (1 << 8)}
        client2 = Client(**parms_dict)
        self.assertIsInstance(Client(), type(client2))
        self.assertEqual(client2.get_parms().poly_modulus_degree(), parms_dict['poly'])
        self.assertEqual(client2.get_parms().plain_modulus().value(), parms_dict['plain'])

    def test_parms(self):
        client3 = Client()
        parms = {"poly": 4096, "coeff": 2048, "plain": (1 << 8)}
        client3.set_parms(**parms)
        self.assertEqual(client3.get_parms().poly_modulus_degree(), parms['poly'])
        self.assertEqual(client3.get_parms().plain_modulus().value(), parms['plain'])

    def test_enc_dec(self):
        arr = np.array([3, 1, 0, -2, -4])
        arr_c = self.client.enc(arr)
        arr_p = self.client.dec(arr_c)
        self.assertTrue(np.array_equal(arr_p, arr))

    def test_mask_with_sign(self):
        arr = np.array([3, 1, 0, -2, -4])
        arr_masked = np.array([1, 1, 0, -1, -1])
        self.assertTrue(np.array_equal(self.client.mask_wth_sign(arr), arr_masked))

    #TODO Add test methods for save and load arrays.
    # Maybe they need to moved to Utils since server will need to use them as well.
