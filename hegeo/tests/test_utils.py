import unittest
from ..utils_computation import wn_point_in_poly
from ..utils_crypto import generate_context
from seal import SEALContext


class UtilsTest(unittest.TestCase):

    def test_wn_point_in_poly(self):
        # Convex U shape facing west
        vertices = [[0, 0], [0, 2], [3, 2], [3, 0], [2, 0], [2, 1], [1, 1], [1, 0]]
        point1 = [1.5, 1.5]  # inside vertical area
        self.assertTrue(wn_point_in_poly(point1, vertices))

        point2 = [1.5, 0.5]  # outside between horizontal areas
        self.assertFalse(wn_point_in_poly(point2, vertices))

        point3 = [4, 2]  # outside above
        self.assertFalse(wn_point_in_poly(point3, vertices))

        point4 = [2.5, 0.5]  # inside top horizontal area
        self.assertTrue(wn_point_in_poly(point4, vertices))

    def test_generate_context(self):
        poly = 2048
        coeff = 2048
        plain = 1 << 8
        context = generate_context(poly, coeff, plain)
        self.assertIsInstance(context, SEALContext)
        context_data = context.key_context_data()
        self.assertEqual(context_data.parms().poly_modulus_degree(), poly)
        self.assertEqual(context_data.parms().plain_modulus().value(), plain)

