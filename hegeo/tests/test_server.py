import unittest
import json
import numpy as np
from ..client import Client
from ..server import Server
from seal import EncryptionParameters, scheme_type, CoeffModulus


class ServerTest(unittest.TestCase):

    server = Server()
    fence = [[-3, -3], [-3, 3], [3, 3], [3, -3]]
    parms = EncryptionParameters(scheme_type.BFV)
    poly_modulus_degree = 4096
    parms.set_poly_modulus_degree(poly_modulus_degree)
    parms.set_coeff_modulus(CoeffModulus.BFVDefault(poly_modulus_degree))
    parms.set_plain_modulus(1 << 8)
    server.set_parms(parms)
    server.fence = fence

    def test_sever(self):
        server1 = Server()
        self.assertIsInstance(Server(), type(server1))

    def test_fence(self):
        self.server.fence = self.fence
        self.assertEqual(self.server.fence, self.fence)

    def test_load_fence(self):
        file_path = "hegeo/tests/resources/sics.json"
        self.server.load_fence(file_path)
        with open(file_path) as file:
            data = (json.load(file)[0]).get('path')
        self.assertEqual(self.server.fence, data)

    def test_sub_array_with_c(self):
        arr = np.array([5, 6, 3, 9, -2, -4, 0])
        client = Client()
        p = np.array([8])
        c = client.enc(p)
        delta = self.server.sub_array_with_c(arr, c[0])
        delta_p = client.dec(delta)
        self.assertTrue(np.array_equal(p-arr, delta_p))

    def test_compute_is_left(self):
        client = Client()
        arr1 = np.array([5, 6, 3, 9, -2, -4, 7])
        arr2 = np.array([6, 8, 3, 9, -2, -4, 5])
        arr1_c = client.enc(arr1)
        arr2_c = client.enc(arr2)
        is_left_c = self.server.compute_is_left(arr1_c, arr2_c)
        is_left_p = client.dec(is_left_c)
        arr1_next = np.roll(arr1, -1)
        arr2_next = np.roll(arr2, -1)
        is_left = arr1 * arr2_next - arr2 * arr1_next
        self.assertTrue(np.array_equal(is_left_p, is_left))

    def test_masking_demasking(self):
        client = Client()
        arr = np.array([39324356456, 144444, 0, -200, -49])
        arr_c = client.enc(arr)
        flag, arr_m = self.server.masking(arr_c)
        arr_m_p = client.dec(arr_m)
        arr_d = self.server.demasking(flag, arr_m_p)
        self.assertTrue(np.array_equal(arr, arr_d))

    def test_detection(self):
        def detection(point_c, fence):
            self.server.fence = fence
            is_left, dy = self.server.compute_intermediate(point_c)
            flag_is_left, is_left_m = self.server.masking(is_left)
            flag_dy, dy_m = self.server.masking(dy)
            is_left = client.dec(is_left_m)
            dy = client.dec(dy_m)
            # is_left = self.server.demasking(flag_is_left, is_left)
            # dy = self.server.demasking(flag_dy, dy)
            return self.server.detect_inclusion(is_left, dy, flag_is_left, flag_dy)


        client = Client()
        vertices = [[0, 0], [0, 20], [30, 20], [30, 0], [20, 0], [20, 10], [10, 10], [10, 0]]

        point1 = [15, 15]  # inside vertical area
        point1_c = client.enc(point1)
        self.assertTrue(detection(point1_c, vertices))

        point2 = [15, 5]   # outside between horizontal areas
        point2_c = client.enc(point2)
        detection(point2_c, vertices)
        self.assertFalse(detection(point2_c, vertices))

        point3 = [40, 20]  # outside above
        point3_c = client.enc(point3)
        self.assertFalse(detection(point3_c, vertices))

        point4 = [25, 5]  # inside top horizontal area
        point4_c = client.enc(point4)
        self.assertTrue(detection(point4_c, vertices))
