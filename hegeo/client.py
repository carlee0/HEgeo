import numpy as np
from seal import Ciphertext, \
    Plaintext, \
    KeyGenerator, \
    CoeffModulus, \
    EncryptionParameters, \
    Encryptor, \
    Decryptor, \
    PublicKey, \
    SecretKey

from .participant import Participant


class Client(Participant):

    def __init__(self):
        super().__init__()
        self._public_key = None
        self._secret_key = None
        self._encryptor = None
        self._decryptor = None
        self.set_parms_from_dict()  # instantiate with default parameters

    def get_parms(self):
        return self._parms

    def set_parms(self, parms: EncryptionParameters, print_parms=False):
        super().set_parms(parms, print_parms)
        keygen = KeyGenerator(self._context)
        self.public_key = keygen.public_key()
        self.secret_key = keygen.secret_key()
        self._encryptor = Encryptor(self._context, self._public_key)
        self._decryptor = Decryptor(self._context, self._secret_key)

    # noinspection PyArgumentList
    def set_parms_from_dict(self, **parms_dict):
        default_parms_dict = {"poly": 4096, "coeff": 4096, "plain": (1 << 8)}
        if parms_dict:
            for key, value in parms_dict.items():
                assert key in parms_dict, "Accepted parameters are poly, coeff, plain, and print_parms"
                default_parms_dict[key] = parms_dict[key]
        self._parms.set_poly_modulus_degree(default_parms_dict['poly'])
        self._parms.set_coeff_modulus(CoeffModulus.BFVDefault(default_parms_dict['coeff']))
        self._parms.set_plain_modulus(default_parms_dict['plain'])
        self.set_parms(self._parms)

    @property
    def public_key(self):
        return self._public_key

    @public_key.setter
    def public_key(self, pk: PublicKey):
        self._public_key = pk

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, sk: SecretKey):
        self._secret_key = sk

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
        arr = np.empty(n, int)
        for i in range(n):
            p = Plaintext()
            self._decryptor.decrypt(cipher_arr[i], p)
            arr[i] = self._encoder.decode_int64(p)
        return arr

    def masking(self, arr):
        assert isinstance(arr, np.ndarray), "Only numpy arrays are accepted"
        return np.sign(arr)
