import numpy as np
from seal import Evaluator, IntegerEncoder, Ciphertext, \
    EncryptionParameters, SEALContext

from .utils_computation import compute_wn


class Server(object):

    def __init__(self):
        self._fence = None
        self._parms = None
        self._context = None
        self._encoder = None
        self._evaluator = None

    @property
    def fence(self):
        return self._fence

    @fence.setter
    def fence(self, fence):
        self._fence = fence

    # noinspection PyCallByClass
    def set_parms(self, parms: EncryptionParameters):
        self._parms = parms
        self._context = SEALContext.Create(self._parms)
        self._encoder = IntegerEncoder(self._context)
        self._evaluator = Evaluator(self._context)

    def compute_intermediate(self, cipher_point):
        assert self.fence is not None, "Geo fence not set"
        assert self._context is not None, "Parameters not set"
        y, x = cipher_point
        vertices = self.fence
        num = len(vertices)

        latitudes = np.array([vertices[i][0] for i in range(num)])
        longitudes = np.array([vertices[i][1] for i in range(num)])

        # Compute dx, dy
        dx = np.empty(num, Ciphertext)
        dy = np.empty(num, Ciphertext)

        for i in range(num):
            c = Ciphertext()
            self._evaluator.sub_plain(x, self._encoder.encode(longitudes[i]), c)
            dx[i] = c

        for i in range(num):
            c = Ciphertext()
            self._evaluator.sub_plain(y, self._encoder.encode(latitudes[i]), c)
            dy[i] = c

        # Compute is_left = dx[i]*dy[j] - dx[j]*dy[i]
        # >0 left, wn++ if direction up
        # =0 line, wn does not change
        # <0 right, wn-- if direction down
        is_left = np.empty(num, Ciphertext)
        for i in range(num):
            j = (i + 1) % num
            c1 = Ciphertext()
            c2 = Ciphertext()
            self._evaluator.multiply(dx[i], dy[j], c1)
            self._evaluator.multiply(dx[j], dy[i], c2)
            self._evaluator.sub_inplace(c1, c2)
            is_left[i] = c1

        return is_left, dy

    @staticmethod
    def masking(self, cipher_array):
        pass

    @staticmethod
    def compute_winding_number(self):
        pass
