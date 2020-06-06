import requests
import hegeo
import os
import sys
import math
import pickle

# http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file


def main(args):

    # TODO: factor out parms_dict?
    # coordinates_p = [59.40430000, 17.95054000] * 1e8
    coordinates_p = [int(math.floor(float(arg)*1e8)) for arg in args[0:2]]
    host = args[2]
    port = args[3]
    url = "http://" + host + ":" + str(port)
    # print("Sending request to: ")
    # print(url)

    # Set up
    he_client = hegeo.Client()
    parms_dict = {"poly": 2048, "coeff": 2048, "plain": (1 << 8)}
    he_client.set_parms_from_dict(**parms_dict)
    coordinates_c = he_client.enc(coordinates_p)

    parms = he_client.get_parms().saves()
    coordinates_s = he_client.save_c_arr(coordinates_c)

    post_variable(url, parms, 'parms')
    post_variable(url, coordinates_s, 'coordinates')

    is_left_string = get_variable(url, "is_left")
    dy_string = get_variable(url, "dy")

    is_left= he_client.load_c_arr(is_left_string)
    dy = he_client.load_c_arr(dy_string)

    is_left_mask, dy_mask = decryt_mask(is_left, dy, he_client)
    is_left_mask_s = pickle.dumps(is_left_mask)
    dy_mask_s = pickle.dumps(dy_mask)

    post_variable(url, is_left_mask_s, "is_left_mask")
    post_variable(url, dy_mask_s, "dy_mask")

    res = get_variable(url, "result")
    print(res.decode())


def post_variable(url, data, data_type):
    url = os.path.join(url, data_type)
    r = requests.post(url, data=data)
    # print(url)
    # print(r.content.decode())


def get_variable(url, data_type):
    url = os.path.join(url, data_type)
    r = requests.get(url)
    # print(url)
    # print(r.status_code)
    return r.content


def decryt_mask(is_left, dy, he_client):
    is_left_dec = he_client.dec(is_left)
    dy_dec = he_client.dec(dy)
    is_left_mask = he_client.masking(is_left_dec)
    dy_mask = he_client.masking(dy_dec)
    return is_left_mask, dy_mask


if __name__ == '__main__':
    assert len(sys.argv) == 5, "Usage: \n" \
                               "$ python client-request.py latitude longitude host port\n" \
                               "ex. $ python client-request.py 59.404500 17.949040 127.0.0.1 5000"
    main(sys.argv[1:])
