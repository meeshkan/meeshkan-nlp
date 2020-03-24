
from meeshkan.nlp.detect_hex import HexDetector
from meeshkan.nlp.gib_detect import GibDetector
#from meeshkan.build.nlp.detect_uuid.detect_uuid import is_valid_uuid
from meeshkan.nlp.detect_uuid import is_valid_uuid
#from detect_uuid.detect_uuid import UUID
import uuid
from enum import Enum

hex_det=HexDetector()
gib_detector=GibDetector()

#Examples
good_list_uuid=[]
for i in range(5):
    good_list_uuid.append(str(uuid.uuid4()))
#print(good_list_uuid)

string = ['14', 'E015', 'jhgjhg', 'house', 'f030c4c11e-41c1-a7eb-3425c53f06d3', '181d4a62-df3e-4e9d-91d8-959b3cf3b' ]+ good_list_uuid


class IdClassifier():

    def __init__(self):
        self.hex_det = HexDetector()
        self.gib_detector = GibDetector()


    def id_classif(self, item):
            try:
                int(item)
                return 'integer'
            except ValueError:
                if is_valid_uuid(item):
                    return 'uuid'
                elif self.gib_detector.gib_detector(item):
                    return 'gib'
                elif self.hex_det.hex_detector(item):
                    return 'hex'
                else:
                    return None

    #id_type=Enum(int, hex, uuid, gib)


    def id_detector(self, string_id):
        id=[]
        for i in string_id:
            if self.id_classif(i) is not None:
                id.append(i)
        if len(id) != 0:
            return id[-1]
        else:
            return None
##print(id_cl.id_classif('khih'))

#print(id_cl.id_detector(string))



