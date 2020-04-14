import typing
from collections import defaultdict

from http_types import HttpExchange
from openapi_typed_2 import (OpenAPIObject, convert_from_openapi,
                             convert_to_openapi)

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.ids.id_classifier import IdClassifier, IdType
from meeshkan.nlp.ids.paths import path_to_regex
from meeshkan.nlp.operation_classifier import OperationClassifier
from meeshkan.nlp.spec_normalizer import SpecNormalizer


class SpecTransformer:
    def __init__(
            self, extractor: EntityExtractor, path_analyzer, normalizer: SpecNormalizer, id_classifier: IdClassifier
    ):
        self._extractor = extractor
        self._path_analyzer = path_analyzer
        self._normalizer = normalizer
        self._operation_classifier = OperationClassifier()
        self._id_classifier = id_classifier

    def optimize_spec(
            self, spec: OpenAPIObject, recordings: typing.List[HttpExchange]
    ) -> OpenAPIObject:
        entity_paths = self._extractor.get_entity_from_spec(spec)
        spec_dict = convert_from_openapi(spec)
        datapaths, spec_dict = self._normalizer.normalize(spec_dict, entity_paths)

        grouped_paths, parameter_names = self._group_paths(spec_dict, recordings)
        spec_dict = self._replace_path_ids(spec_dict, grouped_paths, parameter_names)

        spec_dict = self._operation_classifier.fill_operations(spec_dict)
        spec_dict = self._add_data(spec_dict, datapaths, recordings)

        return convert_to_openapi(spec_dict)

    def _add_data(self, normalized_spec, datapaths, recordings):
        normalized_spec["x-meeshkan-data"] = self._extract_data(datapaths, recordings)
        return normalized_spec

    def _extract_data(self, datapaths, recordings):
        return {}

    def _group_paths(self, spec: typing.Dict, recordings: typing.List[HttpExchange]):
        path_regexs = [(pathname, *path_to_regex(pathname)) for pathname in spec["paths"].keys()]

        res = {pathname: ({param_name: [] for param_name in parameter_names}, list()) for
               pathname, path_regex, parameter_names in path_regexs}

        for rec in recordings:
            for pathname, path_regex, parameter_names in path_regexs:
                values = self._match_to_path(path_regex, pathname)
                if values is not None:
                    res[pathname][1].append(rec)
                    for name, value in zip(parameter_names, values):
                        res[pathname][0][name].append(value)
                    break

        return res, path_regexs[2]

    def _match_to_path(self, path_as_regex, request_path: str) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        match = path_as_regex.match(request_path)

        if match is None:
            return None

        captures = match.groups()
        return captures

    def _replace_path_ids(self, spec, grouped_paths, parameter_names):
        for pathname, (values, recs) in grouped_paths.items():
            for param in reversed(parameter_names):
                res = self._id_classifier.by_values(values[param])
                if res != IdType.UNKNOWN:
                    path_item = spec["paths"].pop(pathname)

                    for param_desc in path_item["parameters"]:
                        if param_desc["name"] == pathname:
                            param_desc["name"] = "id"
                            param_desc["x-meeshkan-id-type"] = res.value
                            break

                    pathname = pathname.replace("{}".format(param), "{id}")
                    spec["paths"][pathname] = path_item
                    break

