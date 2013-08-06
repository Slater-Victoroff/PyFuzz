import fuzzer
import random
import regex_inverter
import Image
import numpy
import StringIO
import binascii
import requests
import lxml.html

BYTE_STRING = lambda raw_file: [int(byte, 16) for byte in raw_file]
IMAGE_STRING = lambda raw_file: [int(byte, 256) for byte in raw_file]

LANGUAGE_MAP = {
    "chinese": "cn",
    "chinese(han)": "cn",
    "dutch": "nl",
    "english": "en",
    "finish": "fin",
    "finnish": "fin",
    "french": "fr",
    "german": "de",
    "greek": "el",
    "herbrew": "il",
    "italian": "it",
    "japanese": "jp",
    "latin": "ltn",
    "polish": "pl",
    "portugese": "pt",
    "russian": "ru",
    "serbian": "sr",
    "spanish": "es"
}


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
        IDHC = BYTE_STRING(result[:14])
        result = result[14:]
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
            result = IDHC+result
            result = [binascii.unhexlify(char[2:]) for char in result]
        if kwargs.get("randomization", False):
            result = IDHC+result
            result = [binascii.unhexlify(hex(char)[2:].zfill(2)) for char in result]
        return "".join(result)
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
            dims = (kwargs["height"], kwargs["width"])
        elif kwargs.get("width", False) or kwargs.get("height", False):
            dim = kwargs.get("width", kwargs["height"])
            dims = (dim, dim)
        else:
            dims = (100, 100)
        kwargs["dims"] = dims
        return func(*args, **kwargs)
    return get_dimensions


def randomize_image(func):
    def get_image(*args, **kwargs):
        try:
            image = Image.open(kwargs["seed"])
        except:
            print "Seed must be a valid file"
            raise
        width, height = image.size

        def change_pixel(color_tuple, location):
            if image.mode == '1':
                value = int(color_tuple[0] >= 127)
            elif image.mode == 'L':
                value = color_tuple[0]
            else:
                value = color_tuple
            image.putpixel((location[0], location[1]), value)

        for i in range(height):
            for j in range(width):
                if random.random() < kwargs.get("mutation_rate", 0.05):
                    color_tuple = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
                    change_pixel(color_tuple, [i, j])
        image.save(kwargs.get("output_file", "randomized.png"))
        return "End"
    return get_image


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


@scale
def random_language(**kwargs):
    """Generates a short snippet of Lorem ipsum in a given language and samples it randomly.

    Generation is done by http://randomtextgenerator.com. This is basically just accessing
    what they've already done and modifying it for this application.
    Currently supported languages are:
    ["chinese(han)", "dutch", "english", "finnish", "french", "german", "greek", "hebrew",
    "italian", "japanese", "latin", "polish", "portugese", "russian", "serbian", "spanish"]"""
    base_url = "http://randomtextgenerator.com"
    language = kwargs.get("language", "polish").lower().strip()
    data = {"text_mode": "plain", "language": LANGUAGE_MAP.get(language, "pl")}
    result = requests.post(base_url, data=data)._content
    document = lxml.html.document_fromstring(result)
    data = document.cssselect('textarea[id="generatedtext"]')[0].text
    return data[:kwargs["length"]]
    # Trying to get this work at lore-ipsum generator, but the scraping is difficult
    # base_url = "http://generator.lorem-ipsum.info"
    # language = kwargs.get("language", "polish").lower().strip()
    # dummy_text = "Lorem ipsum dolor sit amet"
    # data = {"other": language, "link_select": "Go"}
    # data.update({
    #     "language": "other", "radio": "num", "num": "5",
    #     "Rhubarb": "Generate", "type": "plain", "limit": "1000",
    #     "txt": dummy_text, "lang_old": "Latin"})
    # print requests.post(base_url, data=data)._content


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
    if not kwargs.get("seed", False):
        image_array = numpy.random.rand(kwargs["dims"][0], kwargs["dims"][1], 3)*255
        image = Image.fromarray(image_array.astype('uint8')).convert('RGBA')
        format = kwargs.get("format", "PNG")
        output = StringIO.StringIO()
        image.save(output, format=format)
        content = output.getvalue()
        output.close()
    else:
        try:
            content = open(kwargs["seed"], "rb").read()
        except:
            content = kwargs["seed"]
    return [binascii.hexlify(char) for char in content]


@randomize_image
def random_valid_image(**kwargs):
    return None
