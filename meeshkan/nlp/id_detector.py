from meeshkan.nlp.gib_detect import GibDetector
import uuid
from enum import Enum
import string
from typing import Optional


class IdType(Enum):
    #this is the class for id's
    integer = 0
    uuid = 1
    hex = 2
    gib = 3


def is_valid_uuid(id):
    try:
        uuid.UUID(str(id))
        return True
    except ValueError:
        return False

class IdClassifier():

    def __init__(self):
        self.hex_digits = set(string.hexdigits)
        self._gib_detector = GibDetector()


    def id_classif(self, item):
        #this finction return a type of id such as integer, hexadecimal, gibberish or None if it seems to be an english word.
        try:
            int(item)
            return IdType.integer
        except ValueError:
            pass

        if is_valid_uuid(item):
            return IdType.uuid
        elif self._detect_hex(item):
            return IdType.hex
        elif self._gib_detector.gib_detector(item):
            return IdType.gib
        else:
            return None


   

    def id_detector(self, string_id):
        #This function take all the id's from the path list and return the last element if it is exist
        id=[]
        for i in string_id:
            if self.id_classif(i) is not None:
                id.append(i)
        if len(id) != 0:
            return id[-1]
        else:
            return None

    def _detect_hex(self, item):
        #This function return true if it is hexadecimal type of id and False if not.
         if all(c in self.hex_digits for c in item):
             try:
                 int(item, 16)
                 return True

             except ValueError:
                 return False
         else:
             return False


