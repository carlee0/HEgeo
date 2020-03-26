import numpy as np
import seal
from seal import Ciphertext, \
    Decryptor, \
    Encryptor, \
    EncryptionParameters, \
    Evaluator, \
    IntegerEncoder, \
    KeyGenerator, \
    Plaintext, \
    SEALContext


class Client(object):

    def __init__(self, poly=2048, coeff=seal.CoeffModulus.BFVDefault(2048), plain=(1 << 8)):
        encoder, encryptor, decryptor, evaluator = self._generate_params(poly, coeff, plain)
        self._encoder = encoder
        self._encryptor = encryptor
        self._decryptor = decryptor
        self._evaluator = evaluator

    def enc(self, arr_p):
        ctext = []
        for p in arr_p:
            c = Ciphertext()
            self._encryptor.encrypt(self._encoder.encode(p), c)
            ctext.append(c)
        return ctext

    def dec(self, arr_c):
        ptext = []
        for c in arr_c:
            p = Plaintext()
            self._decryptor.decrypt(c, p)
            ptext.append(self._encoder.decode_int32(p))
        return ptext

    def mask_is_left(self, arr_p):
        arr_p = np.array(arr_p)
        return np.sign(arr_p)

    @property
    def encoder(self):
        return self._encoder

    @property
    def evaluator(self):
        return self._evaluator

    def _generate_params(self, poly, coeff, plain):
        # Encryption decryption setup
        parms = EncryptionParameters(seal.scheme_type.BFV)
        parms.set_poly_modulus_degree(poly)
        parms.set_coeff_modulus(coeff)
        parms.set_plain_modulus(plain)

        context = SEALContext.Create(parms)
        # self._print_parameters(context)

        # IntegerEncoder with base b=2, representing integers as polynomials of base b.
        # e.g. 26 = 2^4 + 2^3 + 2^1
        encoder = IntegerEncoder(context)

        keygen = KeyGenerator(context)
        public_key = keygen.public_key()
        secret_key = keygen.secret_key()

        encryptor = Encryptor(context, public_key)
        evaluator = Evaluator(context)
        decryptor = Decryptor(context, secret_key)
        return encoder, encryptor, decryptor, evaluator

    def _print_parameters(self, context):
        print("/ Encryption parameters:")
        print("| poly_modulus: " + context.poly_modulus().to_string())

        # Print the size of the true (product) coefficient modulus
        print("| coeff_modulus_size: " + (str)(context.total_coeff_modulus().significant_bit_count()) + " bits")

        print("| plain_modulus: " + (str)(context.plain_modulus().value()))
        print("| noise_standard_deviation: " + (str)(context.noise_standard_deviation()))

