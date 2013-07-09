import fuzzer
import random
import regex_inverter
import Image
import numpy
import StringIO
import binascii

BYTE_STRING = lambda raw_file: [int(byte, 16) for byte in raw_file]
IMAGE_STRING = lambda raw_file: [int(byte, 256) for byte in raw_file]


def randomize(func):
    def data_generator(*args, **kwargs):
        result = func(*args, **kwargs)
        randomization = kwargs.get("randomization", None)
        if randomization == "byte_jitter":
            result = fuzzer.byte_jitter(
                result,
                kwargs.get("mutation_rate", 0.1)
            )

        elif randomization == "random_chunks":
            result = fuzzer.random_chunks(
                result,
                kwargs.get("mutation_rate", 0.1),
                kwargs.get("mutation_magnitude", 0.1)
            )
        elif randomization == "true_random":
            result = fuzzer.true_random(
                result,
                kwargs.get("mutation_rate", 0.1)
            )
        else:
            result = BYTE_STRING(result)
        return "".join([unichr(number) for number in result])
    return data_generator


def randomize_binary(func):
    def data_generator(*args, **kwargs):
        result = func(*args, **kwargs)
        result = ["0x"+digit for digit in result]
        randomization = kwargs.get("randomization", None)
        if randomization == "byte_jitter":
            result = fuzzer.byte_jitter(
                result,
                kwargs.get("mutation_rate", 0.1)
            )

        elif randomization == "random_chunks":
            result = fuzzer.random_chunks(
                result,
                kwargs.get("mutation_rate", 0.1),
                kwargs.get("mutation_magnitude", 0.1)
            )
        elif randomization == "true_random":
            result = fuzzer.true_random(
                result,
                kwargs.get("mutation_rate", 0.1)
            )
        return "".join([binascii.unhexlify(char[2:]) for char in result])
    return data_generator


def scale(func):
    def find_length(*args, **kwargs):
        if kwargs.get("length", False):
            length = kwargs["length"]
        else:
            length = random.randint(kwargs.get("min_length", 0), kwargs.get("max_length", 1000))
        kwargs["length"] = length
        return func(*args, **kwargs)
    return find_length


def resolution(func):
    def get_dimensions(*args, **kwargs):
        if kwargs.get("width", False) and kwargs.get("height", False):
            dims = (kwargs["width"], kwargs["height"])
        elif kwargs.get("width", False) or kwargs.get("height", False):
            dim = kwargs.get("width", kwargs["height"])
            dims = (dim, dim)
        else:
            dims = (100, 100)
        kwargs["dims"] = dims
        return func(*args, **kwargs)
    return get_dimensions


@randomize
@scale
def random_bytes(**kwargs):
    if kwargs.get("seed", False):
        data = [hex(ord(character)) for character in kwargs["seed"]]
    else:
        data = [hex(random.randint(0, 255)) for unit in range(0, kwargs["length"])]
    return data


@randomize
@scale
def random_ascii(**kwargs):
    if kwargs.get("seed", False):
        data = [hex(ord(character)) for character in kwargs["seed"]]
    else:
        data = [hex(random.randint(0, 127)) for unit in range(kwargs["length"])]
    return data


@randomize
@scale
def random_regex(**kwargs):
    regex = kwargs.get("regex", ".")
    charset = list(regex_inverter.ipermute(regex))
    data = [hex(ord(random.choice(charset))) for unit in range(kwargs["length"])]
    return data


@randomize
@scale
def random_utf8(**kwargs):
    utf_range = lambda start, end: list(range(start, end+1))
    start_bytes = utf_range(0x00, 0x7F) + utf_range(0xC2, 0xF4)
    body_bytes = utf_range(0x80, 0xBF)

    def utf8_char():
        start = random.choice(start_bytes)
        if start <= 0x7F:
            data = [start]
        elif start <= 0xDF:
            data = [start, random.choice(body_bytes)]
        elif start == 0xE0:
            data = [start, random.choice(utf_range(0xA0, 0xBF)), random.choice(body_bytes)]
        elif start == 0xED:
            data = [start, random.choice(utf_range(0x80, 0x9F)), random.choice(body_bytes)]
        elif start <= 0xEF:
            data = [start, random.choice(body_bytes), random.choice(body_bytes)]
        elif start == 0xF0:
            data = [start, random.choice(utf_range(0x90, 0xBF)), random.choice(body_bytes), random.choice(body_bytes)]
        elif start <= 0xF3:
            data = [start, random.choice(body_bytes), random.choice(body_bytes), random.choice(body_bytes)]
        elif start == 0xF4:
            data = [start, random.choice(utf_range(0x80, 0x8F)), random.choice(body_bytes), random.choice(body_bytes)]
        return data
    data = []
    for i in range(kwargs["length"]):
        data.append(str(sum(utf8_char())))
    return data


@randomize_binary
@resolution
def random_image(**kwargs):
    image_array = numpy.random.rand(kwargs["dims"][0], kwargs["dims"][1], 3)*255
    image = Image.fromarray(image_array.astype('uint8')).convert('RGBA')
    format = kwargs.get("format", "PNG")
    output = StringIO.StringIO()
    image.save(output, format=format)
    content = output.getvalue()
    output.close()
    content = [binascii.hexlify(char) for char in content]
    return content

#print random_image(randomization="byte_jitter")
with open("test.png", "wb") as dump:
    dump.write(random_image())

with open("fake.png", 'wb') as dump:
    dump.write(random_image(randomizer="byte_jitter"))
