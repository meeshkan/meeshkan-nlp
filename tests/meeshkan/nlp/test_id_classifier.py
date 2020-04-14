import uuid

from meeshkan.nlp.ids.id_classifier import IdClassifier, IdType


def test_by_value():  # TODO Maria linearize it avoiding cycles
    good_list_uuid = []
    for i in range(5):
        good_list_uuid.append(str(uuid.uuid4()))

    string1 = [
        "14",
        "E015",
        "jhgjhg",
        "house",
        "f030c4c11e-41c1-a7eb-3425c53f06d3",
        "181d4a62-df3e-4e9d-91d8-959b3cf3b",
    ] + good_list_uuid
    ids = [
        "int",
        "hex",
        "random",
        "unknown",
        "random",
        "random",
        "uuid",
        "uuid",
        "uuid",
        "uuid",
        "uuid",  # TODO Maria Make it enum values, i.e. IdType.UUID
    ]

    id_cl = IdClassifier()
    id = []
    for i in string1:
        if id_cl.by_value(i):
            id.append(id_cl.by_value(i).name.lower())
        else:
            id.append(None)
    assert id == ids


def test_by_values():
    id_cl = IdClassifier()

    res = id_cl.by_values(["1", "2", "123", "12455"])
    assert res == IdType.INT

    res = id_cl.by_values(["1", "2", "123", "12455", "outlier"])
    assert res == IdType.INT

    res = id_cl.by_values(["1", "2", "123", "8a6b", "jkvjti944nf"])
    assert res == IdType.RANDOM

    res = id_cl.by_values(["1", "2", "123", "12455", "8a6b"])
    assert res == IdType.HEX

    res = id_cl.by_values(["1", "2", "hello", "world"])
    assert res == IdType.UNKNOWN


def test_by_name():
    id_cl = IdClassifier()

    assert id_cl.by_name("some_id_field")
    assert not id_cl.by_name("some_field")
