import requests
import hegeo
import os
import sys
import math

# http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file

FILE_PATH = 'files'


def main(args):

    # TODO: factor out parms_dict?
    # point = [59.40430000, 17.95054000] * 1e8
    point = [int(math.floor(float(arg)*1e8)) for arg in args[0:2]]
    host = args[2]
    port = args[3]
    url = "http://" + host + ":" + str(port)
    print("Sending request to: ")
    print(url)

    # Set up
    he_client = hegeo.Client()
    parms_dict = {"poly": 2048, "coeff": 2048, "plain": (1 << 8)}
    he_client.set_parms_from_dict(**parms_dict)
    point_c = he_client.enc(point)

    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)

    he_client.get_parms().save(os.path.join(FILE_PATH, 'parms'))
    he_client.save_cipher_array(point_c, os.path.join(FILE_PATH, 'point_size'), os.path.join(FILE_PATH, 'point'))

    post_params(url)
    post_point(url)

    interm_files = {
        'is_left_size': {
            'url': os.path.join(url, "files/is_left_size"),
            'path': os.path.join(FILE_PATH, 'is_left_size')
        },
        'is_left': {
            'url': os.path.join(url, "files/is_left"),
            'path': os.path.join(FILE_PATH, 'is_left')
        },
        'dy_size': {
            'url': os.path.join(url, "files/dy_size"),
            'path': os.path.join(FILE_PATH, 'dy_size')
        },
        'dy': {
            'url': os.path.join(url, "files/dy"),
            'path': os.path.join(FILE_PATH, 'dy')
        }
    }
    get_interm(interm_files)
    decryt_mask(he_client, interm_files, url)


def post_params(url):
    # POST params (server sets params)
    url = os.path.join(url, "set_parms")
    file = open(os.path.join(FILE_PATH, 'parms'), 'rb')
    f = {'file': file}
    try:
        r = requests.post(url, files=f)
    finally:
        file.close()


def post_point(url):
    # POST point (server generates intermediate computation results)
    url = os.path.join(url, "coordinates")
    files = {
        'point_size': open(os.path.join(FILE_PATH, 'point_size'), 'rb'),
        'point': open(os.path.join(FILE_PATH, 'point'), 'rb')
    }
    try:
        r = requests.post(url, files=files)
    finally:
        for f in files.values():
            f.close()


def get_interm(interm_files):
    # GET is_left and dy
    for k in interm_files:
        url = interm_files[k]['url']
        r = requests.get(url)
        with open(interm_files[k]['path'], 'wb') as f:
            f.write(r.content)


def decryt_mask(he_client, interm_files, url):
    # Decrypt and Mask
    is_left = he_client.load_cipher_array(interm_files['is_left_size']['path'], interm_files['is_left']['path'])
    dy = he_client.load_cipher_array(interm_files['dy_size']['path'], interm_files['dy']['path'])
    is_left_dec = he_client.dec(is_left)
    dy_dec = he_client.dec(dy)
    is_left_mask = he_client.masking(is_left_dec)
    dy_mask = he_client.masking(dy_dec)

    he_client.save_array(is_left_mask, os.path.join(FILE_PATH, 'is_left_mask'))
    he_client.save_array(dy_mask, os.path.join(FILE_PATH, 'dy_mask'))

    # POST decrypted and masked results
    url = os.path.join(url, "results")
    files = {
        'is_left_mask': open(os.path.join(FILE_PATH, 'is_left_mask'), 'rb'),
        'dy_mask': open(os.path.join(FILE_PATH, 'dy_mask'), 'rb')
    }
    try:
        r = requests.post(url, files=files)
        print(r.content.decode())
    finally:
        for f in files.values():
            f.close()


if __name__ == '__main__':
    assert len(sys.argv) == 5, "Usage: \n" \
                               "$ python client-request.py latitude longitude host port\n" \
                               "ex. $ python client-request.py 59.404500 17.949040 127.0.0.1 5000"
    main(sys.argv[1:])
