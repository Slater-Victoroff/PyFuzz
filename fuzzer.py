import random
import binascii


BYTE_STRING = lambda raw_file: [int(byte, 16) for byte in raw_file]


def random_chunks(raw_file, mutation_rate, mutation_magnitude):
    """Mutation_rate is the percent of all bytes that will be fuzzed, magnitude is percent of bits fuzzed"""
    values = BYTE_STRING(raw_file)
    for i in range(0, len(values)):
        if random.random() < mutation_rate:
            for j in range(0, 7):
                if random.random() < mutation_magnitude:
                    values[i] ^= 1 << j
    return "".join([chr(number) for number in values])


def byte_jitter(raw_file, mutation_rate):
    """Will XOR random bytes with random numbers in range"""
    values = BYTE_STRING(raw_file)
    for i in range(0, len(values)):
        if random.random() < mutation_rate:
            values[i] ^= random.randint(0, 16)
    return "".join([chr(number) for number in values])


def true_random(raw_file, mutation_rate):
    """Randomly flips bits according to mutation_rate"""
    values = BYTE_STRING(raw_file)
    for i in range(0, len(values)):
        for j in range(0, 7):
            if random.random() < mutation_rate:
                values[i] ^= 1 << j
    return "".join([chr(number) for number in values])


# test = open("sample_unicode").read()
# raw_file = [hex(ord(character)) for character in test]

# print random_chunks(raw_file, 0.5, 0.25)
# print byte_jitter(raw_file, 0.25)
# print true_random(raw_file, 0.1)
