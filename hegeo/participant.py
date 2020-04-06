import numpy as np
import os
import pickle
from abc import ABC, abstractmethod
from seal import EncryptionParameters, \
    SEALContext, \
    Ciphertext, \
    IntegerEncoder, \
    Evaluator, \
    scheme_type


class Participant(ABC):

    def __init__(self):
        self._parms = EncryptionParameters(scheme_type.BFV)
        self._context = None
        self._encoder = None
        self._evaluator = None

    @abstractmethod
    def get_parms(self):
        pass

    # noinspection PyCallByClass,PyArgumentList
    def _set_parms(self, parms: EncryptionParameters, print_parms=False):
        self._parms = parms
        self._context = SEALContext.Create(self._parms)
        self._encoder = IntegerEncoder(self._context)
        self._evaluator = Evaluator(self._context)

        if print_parms:
            self.print_parameters(self._context)

    def load_parms(self, path: str, print_parms=False):
        self._parms.load(path)
        self._set_parms(self._parms, print_parms)
        if print_parms:
            self.print_parameters(self._context)

    @abstractmethod
    def masking(self, arr):
        pass

    def save_cipher_array(self, arr, size_file, binary_file):
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
        # TODO: change np.save to using pickle instead
        # if not size_file.endswith('.npy'):
        #     size_file += '.npy'
        # np.save(size_file, size_array)
        # pickle.dump(size_array, open(size_file, "wb"))
        self.save_array(size_array, size_file)
        os.remove('tmp_file')
        print("Array saved to file: %s\nCorresponding size array saved to file: %s"
              % (binary_file, size_file))

    def load_cipher_array(self, size_file, binary_file):
        # size_array = np.load(size_file)
        # size_array = pickle.load(open(size_file, "rb"))
        size_array = self.load_array(size_file)
        n = len(size_array)
        arr = np.empty(n, object)
        with open(binary_file, 'rb') as fp:
            for i in range(n):
                c = Ciphertext()
                element = fp.read(size_array[i])
                with open('tmp_file', 'wb') as f:
                    f.write(element)
                c.load(self._context, 'tmp_file')
                arr[i] = c
        os.remove('tmp_file')
        return arr

    @staticmethod
    def save_array(arr, file_path):
        """
        Pickles the numpy array and save to file
        :param arr: numpy array
        :param file_path: path to the binary file
        """
        pickle.dump(arr, open(file_path, "wb"))

    @staticmethod
    def load_array(file_path):
        """
        Pickle load the binary file to numpy array
        :param file_path: path to the binary file
        :return: numpy array
        """
        return pickle.load(open(file_path, "rb"))

    @staticmethod
    def print_parameters(context):
        context_data = context.key_context_data()
        print("/ Encryption parameters:")
        print("| poly_modulus: " + str(context_data.parms().poly_modulus_degree()))

        # Print the size of the true (product) coefficient modulus
        coeff_modulus = context_data.parms().coeff_modulus()
        coeff_modulus_sum = 0
        for j in coeff_modulus:
            coeff_modulus_sum += j.bit_count()
        print("| coeff_modulus_size: " + str(coeff_modulus_sum) + " bits")

        print("| plain_modulus: " + str(context_data.parms().plain_modulus().value()))
