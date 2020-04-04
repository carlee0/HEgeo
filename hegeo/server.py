import numpy as np
from seal import Ciphertext

from .participant import Participant


class Server(Participant):

    def __init__(self):
        super().__init__()
        self._fence = None

    @property
    def fence(self):
        return self._fence

    @fence.setter
    def fence(self, fence):
        self._fence = fence

    def get_parms(self):
        return self._parms

    def load_parms(self, path: str, print_parms=False):
        super().load_parms(path, print_parms)

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

    # TODO: Add masking
    def masking(self, cipher_arr):
        pass

    def detect_inclusion(self, is_left_p, dy_p):
        wn = self.compute_wn(is_left_p, dy_p)
        return wn != 0

    # noinspection DuplicatedCode
    @staticmethod
    def compute_wn(is_left_p, dy_p):
        dy_p_next = np.roll(dy_p, -1)
        clockwise = (dy_p <= 0) * (dy_p_next > 0) * is_left_p
        countercl = (dy_p > 0) * (dy_p_next <= 0) * is_left_p

        wn = np.sum(clockwise) + np.sum(countercl)
        return wn
