from py_fuzz.generator import *

print random_language(language="russian")
print random_ascii(
    seed="this is a test", randomization="byte_jitter",
    mutation_rate=0.25
)

print random_regex(
    length=20, regex="[a-zA-Z]"
)

print random_utf8(
    min_length=10,
    max_length=50
)

print random_bytes()
print random_utf8()
print random_regex(regex="[a-zA-Z]")
with open("test.png", "wb") as dump:
    dump.write(random_image())

with open("fake.png", 'wb') as dump:
   dump.write(random_image(randomization="byte_jitter", height=300, width=500, mutation_rate=0))

with open("randomLenna.png", "wb") as dump:
    dump.write("")


random_valid_image(seed="Lenna.png", mutation_rate=0.1)
