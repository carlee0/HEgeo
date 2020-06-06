import numpy as np
import json
from pathlib import Path


def wn_point_in_poly(point, vertices):
    """
    Numerical computation of the winding number algorithm using numpy arrays
    :param point: the point to be tested
    :param vertices: the vertices of the bounding polygon
    :return: (wn != 0) indicating that the point is inside
    """

    num = len(vertices)
    latitudes = np.array([vertices[i][0] for i in range(num)])
    longitudes = np.array([vertices[i][1] for i in range(num)])

    dx = longitudes - point[1]
    dy = latitudes - point[0]
    dx_next = np.roll(dx, -1)
    dy_next = np.roll(dy, -1)

    # is_left
    is_left = dx * dy_next - dx_next * dy
    print(is_left)
    print(dy)
    is_left = np.sign(is_left)

    wn = compute_wn(is_left, dy)
    print("The winding number is: " + str(wn))

    return wn != 0


def compute_wn(is_left_p, dy_p):
    is_left_p = np.array(is_left_p)
    dy_p = np.array(dy_p)
    dy_p_next = np.roll(dy_p, -1)
    clockwise = (dy_p <= 0) * (dy_p_next > 0) * is_left_p
    countercl = (dy_p > 0) * (dy_p_next <= 0) * is_left_p

    wn = np.sum(clockwise) + np.sum(countercl)
    return wn


def import_vertices(file_path):
    assert Path(file_path).suffix != 'json', "file must be a .json file"
    with open(file_path) as file:
        data = json.load(file)[0]
        return data.get('name'), data.get('path')
