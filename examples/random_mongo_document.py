from pyfuzz.generator import random_item


def dummy_document(key, values, **kwargs):
    """
    Returns a document matching the key to a dictionary mapping each value to a random string

    kwargs is passed directly to the random_ascii method of pyfuzz
    """

    dummy_data = {}
    dummy_data[key] = { value: random_item("ascii", **kwargs) for value in values}
    return dummy_data

print dummy_document("_id", ["name", "category", "type"], length=20)
