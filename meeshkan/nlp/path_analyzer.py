import re
from dataclasses import dataclass
from typing import Optional
import spacy

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.ids.gib_detect import GibberishDetector
from meeshkan.nlp.ids.id_classifier import IdClassifier, IdType


@dataclass(frozen=True)
class IdDesc:
    value: Optional[str]
    type: Optional[IdType] = None


@dataclass(frozen=True)
class PathItems:
    entity: Optional[str]
    id: Optional[IdDesc]
    action: Optional[str] = None
    group_id: Optional[IdDesc] = None


class PathAnalyzer:
    def __init__(self, entity_extractor: EntityExtractor):
        self._entity_extractor = entity_extractor
        self._gib_detector = GibberishDetector()
        self._id_classifier = IdClassifier()

    def extract_values(self, path):
        path_list = path.split("/")[1:]
        entity_name = self._entity_extractor.get_entity_from_path(path_list)
        for word in path_list:
            if entity_name in word:
                entity_position = path_list.index(word)
        id_position, id_value, id_type = self._get_last_id(path_list)
        if id_type is not None:
            if id_position > entity_position:
                return PathItems(
                    entity=entity_name, id=IdDesc(value=id_value, type=id_type),
                )
            else:
                return PathItems(entity=entity_name, id=None)
        else:
            return PathItems(entity=entity_name, id=None,)

    def _get_last_id(self, path_items):
        for item in reversed(path_items):
            id_type = self._id_classifier.by_value(item)
            if id_type != IdType.UNKNOWN:
                return path_items.index(item), item, id_type
        return None, None, None
