import unittest
from ..server import Server
from seal import EncryptionParameters, scheme_type, CoeffModulus, \
        SEALContext, IntegerEncoder, Evaluator
# TODO: Check the evaluate function for EncryptionParameters


class ServerTest(unittest.TestCase):

    server = Server()
    fence = [[-3, -3], [-3, 3], [3, 3], [3, -3]]
    parms = EncryptionParameters(scheme_type.BFV)
    parms.set_poly_modulus_degree(2048)
    parms.set_coeff_modulus(CoeffModulus.BFVDefault(2048))
    parms.set_plain_modulus(1<<8)
    server.fence = fence

    def test_sever(self):
        server1 = Server()
        self.assertIsInstance(Server(), type(server1))

    def test_fence(self):
        self.server.fence = self.fence
        self.assertEqual(self.server.fence, self.fence)

    def test_set_parms(self):
        self.server.set_parms(self.parms)
        self.assertIsInstance(self.server._parms, EncryptionParameters)
        self.assertIsInstance(self.server._context, SEALContext)
        self.assertIsInstance(self.server._encoder, IntegerEncoder)
        self.assertIsInstance(self.server._evaluator, Evaluator)

    def test_compute_intermediate(self):
        # TODO: point has to be Ciphertext

        point = None
        self.server.fence = self.fence
        self.server.set_parms(self.parms)
        # is_left, dy = self.server.compute_intermediate(point)

    def test_masking(self):
        pass

    def test_compute_winding_number(self):
        pass


