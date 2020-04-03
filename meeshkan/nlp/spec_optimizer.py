import copy

import typing

from http_types import HttpExchange
from openapi_typed_2 import OpenAPIObject, convert_from_openapi, convert_to_openapi


class SpecOptimizer:
    def __init__(self, extractor, path_analyzer, normalizer):
        self._extractor = extractor
        self._path_analyzer = path_analyzer
        self._normalizer = normalizer

    def optimize_spec(self, spec: OpenAPIObject, recordings: typing.List[HttpExchange]) -> OpenAPIObject:
        spec_dict = copy.deepcopy(convert_from_openapi(spec))

        spec_dict = self._replace_ids(spec_dict, recordings)

        entity_paths = self._group_paths(spec_dict)
        normalized_spec = self._normalize_entities(entity_paths, spec_dict)

        data_spec = self._add_data(entity_paths, normalized_spec, recordings)

        return convert_to_openapi(spec_dict)

    def _replace_ids(self, spec: typing.Dict, recordings: typing.List[HttpExchange]):
        res = dict()
        return spec

    def _group_paths(self, spec):
        return {"account": {"/accounts/v1/accounts"}, "payment": ["/v1/payments/{trnopysd}"]}

    def _normalize_entities(self, entity_paths, spec):
        return spec

    def _add_data(self, entity_paths, normalized_spec, recordings):
        normalized_spec["x-meeshkan-data"] = self._extract_data(entity_paths, normalized_spec, recordings)

    def _extract_data(self, entity_paths, normalized_spec, recordings):
        return {}



