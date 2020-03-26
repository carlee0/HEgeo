import numpy as np


def wn_array(point, vertices):

    num = len(vertices)
    latitudes = np.array([vertices[i][0] for i in range(num)])
    longitudes = np.array([vertices[i][1] for i in range(num)])

    delta_x = longitudes - point[1]
    delta_y = latitudes - point[0]
    delta_x_next = np.roll(delta_x, -1)
    delta_y_next = np.roll(delta_y, -1)

    # is_left
    # >0 left, wn++ if direction up
    # =0 line, wn does not change
    # <0 right, wn-- if direction down
    is_left = delta_x * delta_y_next - delta_x_next * delta_y
    print(is_left)
    is_left = np.sign(is_left)
    print(delta_y)

    clockwise = (delta_y <= 0) * (delta_y_next > 0) * is_left
    countercl = (delta_y > 0) * (delta_y_next <= 0) * is_left
    wn = np.sum(clockwise) + np.sum(countercl)
    print("The winding number is: " + str(wn))
    return wn != 0
