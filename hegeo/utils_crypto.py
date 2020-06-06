from seal import EncryptionParameters, scheme_type, CoeffModulus, SEALContext


def generate_context(poly, coeff, plain, print_parms=False):
    parms = EncryptionParameters(scheme_type.BFV)
    parms.set_poly_modulus_degree(poly)
    parms.set_coeff_modulus(CoeffModulus.BFVDefault(coeff))
    parms.set_plain_modulus(plain)

    context = SEALContext.Create(parms)
    if print_parms:
        print_parameters(context)
    return context


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
