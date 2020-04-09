import requests
import hegeo
import os
# http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file

DATA_PATH = 'data'

# Set up
he_client = hegeo.Client()
parms_dict = {"poly": 2048, "coeff": 2048, "plain": (1 << 8)}
he_client.set_parms_from_dict(**parms_dict)

point = [5940430000, 1795054000]
point_c = he_client.enc(point)
he_client.get_parms().save(os.path.join(DATA_PATH, 'parms'))
he_client.save_cipher_array(point_c, os.path.join(DATA_PATH, 'point_size'), os.path.join(DATA_PATH, 'point'))

# POST params (server sets params)
url = "http://localhost:5000/set_parms"
file = open(os.path.join(DATA_PATH, 'parms'), 'rb')
f = {'file': file}
try:
    r = requests.post(url, files=f)
finally:
    file.close()

# POST point (server generates intermediate computation results)
url = "http://localhost:5000/coordinates"
files = {
    'point_size': open(os.path.join(DATA_PATH, 'point_size'), 'rb'),
    'point': open(os.path.join(DATA_PATH, 'point'), 'rb')
}
try:
    r = requests.post(url, files=files)
finally:
    for f in files.values():
        f.close()


# GET is_left and dy
interm_files = {
    'is_left_size': {
        'url': "http://localhost:5000/files/is_left_size",
        'path': os.path.join(DATA_PATH, 'is_left_size')
    },
    'is_left': {
        'url': "http://localhost:5000/files/is_left",
        'path': os.path.join(DATA_PATH, 'is_left')
    },
    'dy_size': {
        'url': "http://localhost:5000/files/dy_size",
        'path': os.path.join(DATA_PATH, 'dy_size')
    },
    'dy': {
        'url': "http://localhost:5000/files/dy",
        'path': os.path.join(DATA_PATH, 'dy')
    }
}
for k in interm_files:
    url = interm_files[k]['url']
    r = requests.get(url)
    with open(interm_files[k]['path'], 'wb') as f:
        f.write(r.content)

# Decrypt and Mask
is_left = he_client.load_cipher_array(interm_files['is_left_size']['path'], interm_files['is_left']['path'])
dy = he_client.load_cipher_array(interm_files['dy_size']['path'], interm_files['dy']['path'])
is_left_dec = he_client.dec(is_left)
dy_dec = he_client.dec(dy)
is_left_mask = he_client.masking(is_left_dec)
dy_mask = he_client.masking(dy_dec)

he_client.save_array(is_left_mask, os.path.join(DATA_PATH, 'is_left_mask'))
he_client.save_array(dy_mask, os.path.join(DATA_PATH, 'dy_mask'))

# POST decrypted and masked results
url = "http://localhost:5000/results"
files = {
    'is_left_mask': open(os.path.join(DATA_PATH, 'is_left_mask'), 'rb'),
    'dy_mask': open(os.path.join(DATA_PATH, 'dy_mask'), 'rb')
}
try:
    r = requests.post(url, files=files)
    print(r.content.decode())
finally:
    for f in files.values():
        f.close()

