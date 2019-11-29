#!/usr/bin/env python

"""sneaky.py: Hides data into other data."""

__author__ = "D.Tinel"
__copyright__ = "Copyright 2018, DTinel"
__version__ = "1.0.0"
__license__ = "MIT"

import random
import time
import sys

DEFAULT_SEED = long(time.time() * 256)

DEFAULT_ALTERNATIVE_ZERO = u'\u200b'  # ZERO WIDTH SPACE
DEFAULT_ALTERNATIVE_ONE = u'\u200c'  # ZERO WIDTH NON-JOINER


def read(file_name):
    """
    Returns the content of a file.
    :param file_name: The file to read from.
    :return: The content.
    """
    with open(file_name, 'r') as file_obj:
        return file_obj.read().decode('UTF-8')


def write(file_name, content):
    """
    Writes the content to a file.
    :param file_name: The file to write the content to.
    :param content: The content to write.
    """
    with open(file_name, 'w+') as file_obj:
        return file_obj.write(content.encode('UTF-8'))


def char_to_bits(char):
    """
    Returns the binary representation of a character.
    :param char: The character to represent as bits.
    :return: The binary representation as a string value.
    """
    return bin(ord(char))[2:].rjust(8, '0')


def bits_to_char(bits):
    """
    Returns the char representation of 8 bits.
    :param bits: The 8 bits to represent as character.
    :return: The char value.
    """
    return chr(int(bits, 2))


def string_to_bits(text):
    """
    Returns the binary representation of a string.
    :param text: The string to represent as bit sequence.
    :return: The binary representation as a string value.
    """
    return ''.join(map(lambda c: char_to_bits(c), text))


def bits_to_string(text):
    """
    Returns the string representation of a bit sequence.
    :param text: The bit sequence to represent as string.
    :return: The string representation of a bit sequence.
    """
    return ''.join(bits_to_char(text[i:i + 8]) for i in range(0, len(text), 8))


def binary_obfuscation(text, zero=DEFAULT_ALTERNATIVE_ZERO, one=DEFAULT_ALTERNATIVE_ONE):
    """
    Obfuscates a string by converting it to a bit sequence
    with an alternative zero and one.
    :param text: The text to obfuscate.
    :param zero: An alternative binary zero representation.
    :param one:  An alternative binary one representation.
    :return: The obfuscated string.
    """
    text = string_to_bits(text)
    return ''.join(map(lambda c: [zero, one][int(c)], text))


def binary_deobfuscation(secret, zero=DEFAULT_ALTERNATIVE_ZERO, one=DEFAULT_ALTERNATIVE_ONE):
    """
     Reveals the real text behind a string obfuscated as a bit sequence.
     :param secret: The secret text to deobfuscate.
     :param zero: An alternative binary zero representation.
     :param one:  An alternative binary one representation.
     :return: The deobfuscated text.
     """
    secret = ''.join(map(lambda c: {zero: '0', one: '1'}[c], secret))
    return bits_to_string(secret)


def binary_extract(text, zero=DEFAULT_ALTERNATIVE_ZERO, one=DEFAULT_ALTERNATIVE_ONE):
    """
    Extracts two particular characters from a text.
    :param text: The text to extract the characters from.
    :param zero: The first type of character to extract.
    :param one: The second type of character to extract.
    :return: The extracted characters.
    """
    return filter(lambda c: c in [zero, one], text)


def random_char(zero, one, start_range=97, end_range=122):
    """
    Returns a random character except the specified zero and one character.
    :param zero: First excluded character.
    :param one: Second excluded character.
    :param start_range: The random start range.
    :param end_range: The random end range.
    :return: The random character.
    """
    char = random.randint(start_range, end_range)
    while char in [ord(zero), ord(one)]:
        char = random.randint(start_range, end_range)
    return chr(char)


def mix(text_a, text_b, seed=DEFAULT_SEED):
    """
    Mixes two texts randomly together but preserves the order of characters.
    :param text_a: The first text.
    :param text_b: The second text.
    :param seed: The seed.
    :return:
    """
    if len(text_a) > len(text_b):
        temp = text_a
        text_a = text_b
        text_b = temp

    random.seed(seed)
    len_text_a = len(text_a)
    len_text_b = len(text_b)
    output = [None] * (len_text_a + len_text_b)
    len_output = len(output)

    space = len_output // len_text_a
    rest = len_output % len_text_a
    skip = random.randint(0, rest)

    for i in range(0, len_output - rest, space):
        output[skip + i + random.randint(0, space - 1)] = text_a[i / space]

    j = 0
    for i in range(0, len_output):
        if output[i] is None:
            output[i] = text_b[j]
            j += 1

    return ''.join(output)


def hide(secret, data, zero=DEFAULT_ALTERNATIVE_ZERO, one=DEFAULT_ALTERNATIVE_ONE, seed=DEFAULT_SEED):
    """
    Hides a secret into other data.
    :param secret: The secret to hide.
    :param data: The data that hides the secret.
    :param zero: An alternative binary zero representation.
    :param one:  An alternative binary one representation.
    :param seed: The seed for the random mixing.
    :return: The data containing the hided secret.
    """
    return mix(binary_obfuscation(secret, zero, one), data, seed)


def hide_random(secret,
                zero=DEFAULT_ALTERNATIVE_ZERO,
                one=DEFAULT_ALTERNATIVE_ONE,
                data_seed=DEFAULT_SEED,
                mix_seed=DEFAULT_SEED):
    """
    Hides a secret into random data.
    :param secret: The secret to hide.
    :param zero: An alternative binary zero representation.
    :param one:  An alternative binary one representation.
    :param data_seed: The seed for the random data.
    :param mix_seed: The seed for the random mixing.
    :return: The random data containing the secret.
    """
    random.seed(data_seed)
    data = ''.join([random_char(zero, one) for i in range(len(secret) * 16)])
    return hide(secret, data, zero, one, mix_seed)


def reveal(data, zero=DEFAULT_ALTERNATIVE_ZERO, one=DEFAULT_ALTERNATIVE_ONE):
    """
    Reveals the secret that is hidden into the specified data.
    :param data: The data that contains the secret.
    :param zero: An alternative binary zero representation.
    :param one:  An alternative binary one representation.
    :return: The secret.
    """
    return binary_deobfuscation(binary_extract(data, zero, one), zero, one)


def obfuscate_file(secret_file, normal_file, output_file,
                   zero=DEFAULT_ALTERNATIVE_ZERO,
                   one=DEFAULT_ALTERNATIVE_ONE):
    """

    :param secret_file: The file containing the secret.
    :param normal_file: The file that hides the secret.
    :param output_file: The output file that will contain
                        the normal data with the hidden secret.
    :param zero: An alternative binary zero representation.
    :param one: An alternative binary one representation.
    """
    secret = read(secret_file)
    data = read(normal_file)
    result = hide(secret, data, zero, one)
    write(output_file, result)


def deobfuscate_file(input_file, output_file,
                     zero=DEFAULT_ALTERNATIVE_ZERO,
                     one=DEFAULT_ALTERNATIVE_ONE):
    """

    :param input_file: The obfuscated file containing the secret.
    :param output_file: The output that will be the secret.
    :param zero: An alternative binary zero representation.
    :param one: An alternative binary one representation.
    """
    data = read(input_file)
    result = reveal(data, zero, one)
    write(output_file, result)


def example():
    """
    Example code
    """
    message = "this is a secret text"
    print("Message: " + message)

    zero = 'z'  # An alternative binary zero.
    one = 'o'  # An alternate binary one.
    print("Properties: 0 = " + zero + ", 1 = " + one)

    obfuscated = hide_random(message, zero, one)
    print("Obfuscated: " + obfuscated)

    deobfuscated = reveal(obfuscated, zero, one)
    print("Deobfuscated: " + deobfuscated)


def info():
    """
    Prints information about this script.
    """
    print("================== SNEAKY ==================")
    print("Author: D.Tinel")
    print("Version: 1.0.0")
    print("License: MIT")
    print("============================================")
    print("")
    print("# Shows an example.")
    print("sneaky.py example")
    print("")
    print("# Hides a secret file into another file.")
    print("sneaky.py hide <file_secret> <file_normal> <file_output> <zero_char> <one_char>")
    print("")
    print("# Reveals the secret in a file.")
    print("sneaky.py reveal <file_input> <file_output> <zero_char> <one_char>")


def main(args):
    """
    The main function.
    :param args: The command line arguments.
    """
    if len(args) == 2 and args[1] == "example":
        example()
    elif len(args) == 7 and args[1] == "hide":
        obfuscate_file(args[2], args[3], args[4], args[5], args[6])
    elif len(args) == 6 and args[1] == "reveal":
        deobfuscate_file(args[2], args[3], args[4], args[5])
    elif len(args) > 1:
        sys.stderr.write("Invalid arguments\n")
    else:
        info()


if __name__ == "__main__":
    main(sys.argv)
