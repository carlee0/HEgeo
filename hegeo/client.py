import numpy as np
import os
from seal import Ciphertext, \
    Decryptor, \
    Encryptor, \
    Evaluator, \
    IntegerEncoder, \
    KeyGenerator, \
    Plaintext, \
    scheme_type, \
    EncryptionParameters, \
    CoeffModulus, \
    SEALContext


class Client(object):

    def __init__(self, print_parms=False, **parms_dict):
        # default parameters
        self._parms_dict = {"poly": 2048, "coeff": 2048, "plain": (1 << 8)}
        self._parms = EncryptionParameters(scheme_type.BFV)
        self._context = None
        self._public_key = None
        self._secret_key = None
        self._encoder = None
        self._encryptor = None
        self._decryptor = None
        self._evaluator = None

        if parms_dict:
            self.set_parms(**parms_dict)
        else:
            self.set_parms(**self._parms_dict)

    def get_parms(self):
        return self._parms

    def set_parms(self, **parms):
        for key, value in parms.items():
            assert key in parms, "Accepted parameters are poly, coeff and plain"
            self._parms_dict[key] = parms[key]

        self._parms.set_poly_modulus_degree(self._parms_dict['poly'])
        self._parms.set_coeff_modulus(CoeffModulus.BFVDefault(self._parms_dict['coeff']))
        self._parms.set_plain_modulus(self._parms_dict['plain'])

        self._context = SEALContext.Create(self._parms)
        keygen = KeyGenerator(self._context)
        self._public_key = keygen.public_key()
        self._secret_key = keygen.secret_key()
        self._encoder = IntegerEncoder(self._context)
        self._encryptor = Encryptor(self._context, self._public_key)
        self._decryptor = Decryptor(self._context, self._secret_key)
        self._evaluator = Evaluator(self._context)

    def get_public_key(self):
        return self._public_key

    def get_secret_key(self):
        return self._secret_key

    def enc(self, arr):
        n = len(arr)
        cipher_arr = np.empty(n, Ciphertext)
        for i in range(n):
            c = Ciphertext()
            self._encryptor.encrypt(self._encoder.encode(arr[i]), c)
            cipher_arr[i] = c
        return cipher_arr

    def dec(self, cipher_arr):
        n = len(cipher_arr)
        arr = np.empty(n, Plaintext)
        for i in range(n):
            p = Plaintext()
            self._decryptor.decrypt(cipher_arr[i], p)
            arr[i] = self._encoder.decode_int64(p)
        return arr

    @staticmethod
    def mask_wth_sign(arr):
        assert isinstance(arr, np.ndarray), "Only numpy arrays are accepted"
        return np.sign(arr)

    @staticmethod
    def save_array(arr, size_file, binary_file):
        assert isinstance(arr[0], object)  # must be Plaintext or Ciphertext arrays
        n = len(arr)
        size_array = np.empty(n, int)
        with open(binary_file, 'wb') as fp:
            for i in range(n):
                arr[i].save('tmp_file')
                with open('tmp_file', 'rb') as f:
                    element = f.read()
                    size_array[i] = len(element)
                fp.write(element)
        if not size_file.endswith('.npy'):
            size_file += '.npy'
        np.save(size_file, size_array)
        os.remove('tmp_file')
        print("Array saved to file: %s\n Corresponding size array saved to file: %s"
              % (binary_file, size_file))

    @staticmethod
    def load_array(context: SEALContext, size_file, binary_file):
        size_array = np.load(size_file)
        n = len(size_array)
        arr = np.empty(n, object)
        with open(binary_file, 'rb') as fp:
            for i in range(n):
                c = Ciphertext()
                element = fp.read(size_array[i])
                with open('tmp_file', 'wb') as f:
                    f.write(element)
                c.load(context, 'tmp_file')
                arr[i] = c
        os.remove('tmp_file')
        return arr

