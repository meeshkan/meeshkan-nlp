import copy
import typing

from http_types import HttpExchange

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.entity_normalizer import EntityNormalizer
from meeshkan.nlp.operation_classifier import OperationClassifier
from openapi_typed_2 import (OpenAPIObject, convert_from_openapi,
                             convert_to_openapi)


class SpecOptimizer:
    def __init__(
        self, extractor: EntityExtractor, path_analyzer, normalizer: EntityNormalizer
    ):
        self._extractor = extractor
        self._path_analyzer = path_analyzer
        self._normalizer = normalizer
        self._operation_classifier = OperationClassifier()

    def optimize_spec(
        self, spec: OpenAPIObject, recordings: typing.List[HttpExchange]
    ) -> OpenAPIObject:
        entity_paths = self._extractor.get_entity_from_spec(spec)
        spec_dict = convert_from_openapi(spec)
        spec_dict = self._replace_ids(spec_dict, recordings)
        datapaths, spec_dict = self._normalizer.normalize(spec_dict, entity_paths)
        spec_dict = self._operation_classifier.fill_operations(spec_dict)
        spec_dict = self._add_data(spec_dict, datapaths, recordings)

        return convert_to_openapi(spec_dict)

    def _replace_ids(self, spec: typing.Dict, recordings: typing.List[HttpExchange]):
        res = dict()
        return spec

    def _add_data(self, normalized_spec, datapaths, recordings):
        normalized_spec["x-meeshkan-data"] = self._extract_data(datapaths, recordings)
        return normalized_spec

    def _extract_data(self, datapaths, recordings):
        return {}
