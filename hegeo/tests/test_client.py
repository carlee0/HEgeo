import unittest
from ..client import Client


class ClientTest(unittest.TestCase):

    client = Client()

    def test_client(self):
        self.assertIsInstance(Client(), type(self.client))

    def test_enc_dec(self):
        arr = [3, 1, 0, -2, -4]
        arr_c = self.client.enc(arr)
        arr_p = self.client.dec(arr_c)
        self.assertEqual(arr_p, arr)

    def test_mask_is_left(self):
        arr = [3, 1, 0, -2, -4]
        arr_masked = [1, 1, 0, -1, -1]
        for i in range(len(arr)):
            self.assertEqual(self.client.mask_is_left(arr)[i], arr_masked[i])




