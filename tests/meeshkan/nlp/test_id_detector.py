import uuid

from meeshkan.nlp.ids.id_classifier import IdClassifier


def test_id_detector():
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
        "integer",
        "hex",
        "gib",
        None,
        "gib",
        "gib",
        "uuid",
        "uuid",
        "uuid",
        "uuid",
        "uuid",
    ]

    id_cl = IdClassifier()
    id = []
    for i in string1:
        if id_cl.by_value(i):
            id.append(id_cl.by_value(i).name)
        else:
            id.append(None)
    assert id == ids
