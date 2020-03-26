import numpy as np
import copy

from seal import Plaintext


class Server(object):

    def __init__(self, fence=None, encoder=None, evaluator=None):
        self._fence = fence
        # self._encoder = encoder
        self._evaluator = evaluator

    @property
    def fence(self):
        return self._fence

    @fence.setter
    def fence(self, fence):
        self._fence = fence

    # @property
    # def encoder(self):
    #     return self._encoder
    #
    # @encoder.setter
    # def encoder(self, encoder):
    #     self._encoder = encoder  # probably not neccessary

    @property
    def evaluator(self):
        return self._evaluator

    @evaluator.setter
    def evaluator(self, evaluator):
        self._evaluator = evaluator

    def compute_intermediate(self, point):
        y, x = point
        vertices = self.fence
        num = len(vertices)

        latitudes = np.array([vertices[i][0] for i in range(num)])
        longitudes = np.array([vertices[i][1] for i in range(num)])

        self.evaluator.negate_inplace(x)
        self.evaluator.negate_inplace(y)

        # Compute delta and delta_next
        dx = []
        dy = []

        for i in range(len(vertices)):
            x_copy = copy.deepcopy(x)
            self._evaluator.add_plain(x_copy, self._encoder.encode(longitudes[i]))
            # lon_p = Plaintext(str(longitudes[i]))
            # self._evaluator.add_plain(x_copy, lon_p, x_copy)
            dx.append(x_copy)

        # TODO: Add support for signed integer
        for i in range(len(vertices)):
            y_copy = copy.deepcopy(y)
            self._evaluator.add_plain(y_copy, self._encoder.encode(latitudes[i]))
            # lat_p = Plaintext(str(latitudes[i]))
            # self._evaluator.add_plain(y_copy, lat_p, y_copy)
            dy.append(y_copy)

        dx = np.array(dx)
        dy = np.array(dy)

        # Compute is_left, value stored at delta_x
        dx_next = np.roll(copy.deepcopy(dx), -1)
        dy_next = np.roll(copy.deepcopy(dy), -1)

        for i in range(len(vertices)):
            self._evaluator.multiply_inplace(dx[i], dy_next[i])
            self._evaluator.multiply_inplace(dx_next[i], dy[i])
            self._evaluator.negate_inplace(dx_next[i])
            self._evaluator.add_inplace(dx[i], dx_next[i])

        return dx, dy

    def compute_wn(self, is_left_p, dy_p):
        dy_p_next = np.roll(dy_p, -1)
        clockwise = (dy_p <= 0) * (dy_p_next > 0) * is_left_p
        countercl = (dy_p > 0) * (dy_p_next <= 0) * is_left_p

        wn = np.sum(clockwise) + np.sum(countercl)
        print("The winding number is: " + str(wn))
        return (wn != 0)