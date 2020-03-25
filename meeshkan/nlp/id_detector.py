
from meeshkan.nlp.detect_hex import HexDetector
from meeshkan.nlp.gib_detect import GibDetector
#from meeshkan.build.nlp.detect_uuid.detect_uuid import is_valid_uuid
from meeshkan.nlp.detect_uuid import is_valid_uuid
#from detect_uuid.detect_uuid import UUID
import uuid
from enum import Enum

class IdType(Enum):
    integer=0
    uuid=1


class IdClassifier():

    def __init__(self):
        self._hex_d = HexDetector()
        self._gib_detector = GibDetector()


    def id_classif(self, item):
            try:
                int(item)
                return IdType.integer
            except ValueError:
                if is_valid_uuid(item):
                    return 'uuid'
                elif self.hex_det.hex_detector(item):
                    return 'hex'
                elif self.gib_detector.gib_detector(item):
                    return 'gib'
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

    def _detect_hex(self, item):
         if all(c in self.hex_digits for c in item):
             try:
                 int(item, 16)
                 return True

             except ValueError:
                 return False
         else:
             return False
##print(id_cl.id_classif('khih'))

#print(id_cl.id_detector(string))



