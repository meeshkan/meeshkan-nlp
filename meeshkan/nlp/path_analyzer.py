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
    type: Optional[
        IdType
    ] = None


@dataclass(frozen=True)
class PathItems:
    entity: Optional[str]
    id: Optional[IdDesc]
    action: Optional[str]=None
    group_id: Optional[IdDesc]=None


class PathAnalyzer:
    def __init__(self, entity_extractor: EntityExtractor):
        self._entity_extractor = entity_extractor
        self._gib_detector = GibberishDetector()
        self._id_classifier = IdClassifier()

    def extract_values(self, path):
        path_list = path.split("/")[1:]
        nopunc_string = []
        for i in path_list:
            if self._id_classifier.by_value(i) is not None:
                nopunc_string.append(i)
            else:
                i = re.sub("[^0-9a-z]+", " ", i.lower())
                for word in i.split(" "):
                    nopunc_string.append(word)
        pos = {
            value: index for index, value in enumerate(nopunc_string)
        }
        print(pos)# TODO Maria You can avoid this if you return indexes from get_last_id instead of values
        maybe_entity = self._entity_extractor._split_pathes(path_list)[
            -1
        ]  # TODO Maria a public method name can't start with an underscore. And it does something different from splitting paths.
        id_value, id_type = self._get_last_id(path_list)
        if id_type != IdType.UNKNOWN:
            if pos[id_value] == pos[maybe_entity] + 1:
                return PathItems(
                    entity=self._entity_extractor.get_entity_from_url(path_list),
                    id=IdDesc(value=id_value, type=id_type),
                )
            else:
                return PathItems(
                    entity=self._entity_extractor.get_entity_from_url(path_list),
                )
        else:
            return PathItems(
                entity=self._entity_extractor.get_entity_from_url(path_list),
                id=None,
            )

    def _get_last_id(self, path_items):
        for item in reversed(path_items):
            id_type = self._id_classifier.by_value(item)
            if id_type is not None:
                return item, id_type

        return None, None


nlp=spacy.load('en_core_web_lg')
analyzer= PathAnalyzer(nlp)
path_item1 = analyzer.extract_values(
        "/v3/profiles/saf45gdrg4gsdf/transfers/sdfsr456ygh56ujhgf/payments"
    )
print(path_item1)