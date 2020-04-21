import typing
from operator import itemgetter

from http_types import HttpExchange
from jsonpath_rw import parse
from openapi_typed_2 import OpenAPIObject, convert_from_openapi, convert_to_openapi

from meeshkan.nlp.data_extractor import DataExtractor
from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.ids.id_classifier import IdClassifier, IdType
from meeshkan.nlp.operation_classifier import OperationClassifier
from meeshkan.nlp.spec_normalizer import SpecNormalizer


class SpecTransformer:
    def __init__(
        self,
        extractor: EntityExtractor,
        path_analyzer,
        normalizer: SpecNormalizer,
        id_classifier: IdClassifier,
    ):
        self._extractor = extractor
        self._path_analyzer = path_analyzer
        self._normalizer = normalizer
        self._operation_classifier = OperationClassifier()
        self._id_classifier = id_classifier
        self._data_extractor = DataExtractor()

    def optimize_spec(
        self, spec: OpenAPIObject, recordings: typing.List[HttpExchange]
    ) -> OpenAPIObject:
        entity_paths = self._extractor.get_entity_from_spec(spec)
        spec_dict = convert_from_openapi(spec)
        datapaths, spec_dict = self._normalizer.normalize(spec_dict, entity_paths)

        grouped_records = self._data_extractor.group_records(spec_dict, recordings)
        spec_dict = self._replace_path_ids(spec_dict, grouped_records)

        spec_dict = self._operation_classifier.fill_operations(spec_dict)
        data = self._data_extractor.extract_data(datapaths, grouped_records)
        spec_dict = self._add_entity_ids(spec_dict, data)
        spec_dict = self._inject_data(spec_dict, data)
        return convert_to_openapi(spec_dict)

    def _replace_path_ids(self, spec, grouped_records):
        for pathname, path_record in grouped_records.items():
            for param in reversed(path_record.path_args):
                res = self._id_classifier.by_values(path_record.path_arg_values[param])
                if res != IdType.UNKNOWN:
                    path_item = spec["paths"].pop(pathname)

                    for param_desc in path_item["parameters"]:
                        if param_desc["name"] == param:
                            param_desc["name"] = "id"
                            param_desc["x-meeshkan-id-type"] = res.value
                            break

                    pathname = pathname.replace("{{{}}}".format(param), "{id}")
                    spec["paths"][pathname] = path_item
                    break

        return spec

    def _add_entity_ids(self, spec_dict, data):
        for name, values in data.items():
            schema = spec_dict["components"]["schemas"][name]
            potential_ids = []
            for property in schema["properties"]:
                name_score = self._id_classifier.by_name(name, property)
                if name_score > 0:
                    res = self._id_classifier.by_values(
                        (v[property] for v in values if property in v)
                    )
                    if res != IdType.UNKNOWN:
                        potential_ids.append((property, res, name_score))

            if len(potential_ids) > 0:
                idx = max(potential_ids, key=itemgetter(2))
                schema["x-meeshkan-id-path"] = idx[0]
                schema["x-meeshkan-id-type"] = idx[1].value

        return spec_dict

    def _inject_data(self, spec_dict, data):
        spec_dict["x-meeshkan-data"] = {}
        for name, values in data.items():
            expr = parse(spec_dict["components"]["schemas"][name]["x-meeshkan-id-path"])
            injected_values = dict()
            for val in values:
                idx = expr.find(val)
                if len(idx) > 0:
                    injected_values[idx[0].value] = val

            spec_dict["x-meeshkan-data"][name] = list(injected_values.values())

        return spec_dict
