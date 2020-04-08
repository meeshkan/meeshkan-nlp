import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.gib_detect import GibDetector
from meeshkan.nlp.id_detector import IdClassifier, IdType


@dataclass(frozen=True)
class IdDesc:
    value: Optional[str]
    type: Optional[IdType]


@dataclass(frozen=True)
class PathItems:
    entity: Optional[str]
    action: Optional[str]
    id: Optional[IdDesc]
    group_id: Optional[IdDesc]


class PathAnalyzer:
    def __init__(self, entity_extractor: EntityExtractor):
        self._entity_extractor = entity_extractor
        self._gib_detector = GibDetector()
        self._id_classifier = IdClassifier()

    def extract_values(self, path):
        path_list = path.split("/")[1:]
        nopunc_string = []
        for i in path_list:
            if self._id_classifier.id_classif(i) is not None:
                nopunc_string.append(i)
            else:
                i = re.sub("[^0-9a-z]+", " ", i.lower())
                for word in i.split(" "):
                    nopunc_string.append(word)
        pos = {value: index for index, value in enumerate(nopunc_string)}
        maybe_entity = self._entity_extractor._split_pathes(path_list)[-1]
        maybe_id = self._id_classifier.id_detector(path_list)
        if maybe_id is not None:
            if pos[maybe_id] == pos[maybe_entity] + 1:
                return PathItems(
                    entity=self._entity_extractor.get_entity_from_url(path_list),
                    id=IdDesc(
                        value=maybe_id, type=self._id_classifier.id_classif(maybe_id)
                    ),
                    action=None,
                    group_id=None,
                )
            else:
                return PathItems(
                    entity=self._entity_extractor.get_entity_from_url(path_list),
                    id=None,
                    action=None,
                    group_id=None,
                )
        else:
            return PathItems(
                entity=self._entity_extractor.get_entity_from_url(path_list),
                id=None,
                action=None,
                group_id=None,
            )
