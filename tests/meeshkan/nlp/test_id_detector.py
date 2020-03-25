

def test_id_detector():
    hex_det = HexDetector()
    gib_detector = GibDetector()

    # Examples
    good_list_uuid = []
    for i in range(5):
        good_list_uuid.append(str(uuid.uuid4()))
    # print(good_list_uuid)

    string = ['14', 'E015', 'jhgjhg', 'house', 'f030c4c11e-41c1-a7eb-3425c53f06d3',
              '181d4a62-df3e-4e9d-91d8-959b3cf3b'] + good_list_uuid

def test_hes_detector():

