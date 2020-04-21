import string
import typing
import uuid
from enum import Enum

from meeshkan.nlp.ids.gib_detect import GibberishDetector


class IdType(Enum):
    UNKNOWN = "unknown"
    INT = "int"
    UUID = "uuid"
    HEX = "hex"
    RANDOM = "random"


class IdClassifier:
    _hex_digits = set(string.hexdigits)

    def __init__(self):
        self._gib_detector = GibberishDetector()

    def by_values(self, values: typing.Iterable[str]) -> IdType:
        total_values = 0.0
        unknown_values = 0.0
        max_id_type = IdType.UNKNOWN
        for value in values:
            total_values += 1
            id_type = self.by_value(value)
            if id_type == IdType.UNKNOWN:
                unknown_values += 1
            else:
                max_id_type = id_type if id_type.value > max_id_type.value else id_type

        score = (total_values - unknown_values) / total_values

        return max_id_type if score > 0.7 else IdType.UNKNOWN

    def by_name(self, entity: str, name: str) -> float:
        name = name.lower()
        if name == "id":
            return 0.9
        elif "id" in name:
            return 0.8 if entity in name else 0.6
        else:
            return 0

    def by_value(self, value: str) -> IdType:
        if self._is_int(value):
            return IdType.INT
        if self._is_valid_uuid(value):
            return IdType.UUID
        elif self._is_hex(value):
            return IdType.HEX
        elif self._gib_detector.is_gibberish(value):
            return IdType.RANDOM
        else:
            return IdType.UNKNOWN

    def _is_hex(self, value):
        if all(c in self._hex_digits for c in value):
            try:
                int(value, 16)
                return True

            except ValueError:
                return False
        else:
            return False

    def _is_valid_uuid(self, value):
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    def _is_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False
