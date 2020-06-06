from pathlib import Path
import json

import numpy as np
from seal import Ciphertext

from .participant import Participant


class Server(Participant):

    def __init__(self):
        super().__init__()
        self._fence = None
        self._flag_is_left = None
        self._flag_dy = None

    @property
    def fence(self):
        return self._fence

    @fence.setter
    def fence(self, fence):
        self._fence = fence

    def load_fence(self, file_path):
        """ import coordinates from file
            Args:
              file_path -- file path
                example .txt file:
                    59.4048184072506,17.9478923473923
                    59.4043815528131,17.9485360775559
                    59.404422508156,17.9486433659165
                example .json file can be created at http://geo.jasparke.net/
                    [
                        {
                            "name": "sics",
                            "color": "#6CB1E1",
                            "id": 0,
                            "path": [[59.4048182070281, 17.9478945561005],
                                    [59.4043772570510, 17.9485382862641],
                                    [59.4046025108524, 17.9491310544564],
                                    [59.4046598479445, 17.949050588186],]
                        }
                    ]
            Returns:
                name of the site from .json files or "site" as default for .txt files
                geo coordinates of the vertices [[lat0, lon0], [lat1, lon1], ...]
            """
        try:
            with open(file_path) as file:
                if Path(file_path).suffix == '.json':
                    data = json.load(file)[0]
                    self.fence = data.get('path')
                elif Path(file_path).suffix == '.txt':
                    lines = file.readlines()
                    self.fence = []
                    for line in lines:
                        self.fence.append([float(x) for x in line.strip().split(',')])
                else:
                    raise ValueError("File type not supported")
        except FileNotFoundError:
            raise
        except ValueError:
            raise

    # def get_parms(self):
    #     return self._parms

    # def load_parms(self, path: str, print_parms=False):
    #     super().load_parms(path, print_parms)

    def compute_intermediate(self, cipher_point):
        assert self.fence is not None, "Geo fence not set"
        assert self._context is not None, "Parameters not set"
        y, x = cipher_point
        vertices = self.fence
        num = len(vertices)

        latitudes = np.array([vertices[i][0] for i in range(num)])
        longitudes = np.array([vertices[i][1] for i in range(num)])

        dx = self.sub_array_with_c(longitudes, x)
        dy = self.sub_array_with_c(latitudes, y)

        is_left = self.compute_is_left(dx, dy)

        return is_left, dy

    def sub_array_with_c(self, arr, cipher):
        """
        Utility function for compute differentials dx and dy
        :param arr: Numpy array
        :param cipher: Integer in Ciphertext
        :return: array of ciphertext of (cipher-arr)
        """
        num = len(arr)
        delta = np.empty(num, Ciphertext)
        for i in range(num):
            c = Ciphertext()
            self._evaluator.sub_plain(cipher, self._encoder.encode(arr[i]), c)
            delta[i] = c
        return delta

    def compute_is_left(self, dx, dy):
        """
        Compute is_left = dx[i]*dy[j] - dx[j]*dy[i]
        # >0 left, wn++ if direction up
        # =0 line, wn does not change
        # <0 right, wn-- if direction down
        :param dx: Array of Ciphertext
        :param dy: Array of Ciphertext
        :return: Arry of Ciphertext is_left
        """
        assert len(dx) == len(dy)
        num = len(dx)
        is_left = np.empty(num, Ciphertext)
        for i in range(num):
            j = (i + 1) % num
            c1 = Ciphertext()
            c2 = Ciphertext()
            self._evaluator.multiply(dx[i], dy[j], c1)
            self._evaluator.multiply(dx[j], dy[i], c2)
            self._evaluator.sub_inplace(c1, c2)
            is_left[i] = c1
        return is_left

    def masking(self, cipher_arr):
        """
        Mask the cipher_arr with a sign change
        :param cipher_arr: the cipher_arr to mask
        :return: masked cipher_arr
        """
        num = len(cipher_arr)
        flag = np.random.choice([-1, 1], num)

        for i in range(num):
            self._evaluator.multiply_plain_inplace(cipher_arr[i], self._encoder.encode(flag[i]))
        return flag, cipher_arr

    def demasking(self, flag, arr):
        """
        Demask the arr masked with the flag that was used to mask the cipher array
        :param flag: Array of integers in {-1, 1}, same length as cipher_arr
        :param arr: Numpy array to demask
        :return: demasked arr
        """
        assert len(flag) == len(arr), "Flag and the cipher array must have the same length"
        return flag * arr

    def detect_inclusion(self, is_left_p, dy_p, is_left_flag=None, dy_flag=None):
        if (type(is_left_flag) is np.ndarray) and (type(dy_flag) is np.ndarray):
            assert len(is_left_flag) == len(dy_flag), "Length of the flag arrays must match"
            assert len(is_left_p) == len(is_left_flag) or len(dy_p) == len(dy_flag), \
                "Length of arrays must match"
            is_left_p = is_left_p * is_left_flag
            dy_p = dy_p * dy_flag
        wn = self.compute_wn(is_left_p, dy_p)
        return wn != 0

    # noinspection DuplicatedCode
    @staticmethod
    def compute_wn(is_left_p, dy_p):
        dy_p_next = np.roll(dy_p, -1)
        clockwise = (dy_p <= 0) * (dy_p_next > 0) * np.sign(is_left_p)
        countercl = (dy_p > 0) * (dy_p_next <= 0) * np.sign(is_left_p)

        wn = np.sum(clockwise) + np.sum(countercl)
        return wn
