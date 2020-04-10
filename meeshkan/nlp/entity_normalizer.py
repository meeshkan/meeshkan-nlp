import itertools
import typing
from typing import Tuple

import jsonpath_rw
from openapi_typed_2 import (
    OpenAPIObject,
    convert_from_openapi,
    dataclass,
    convert_to_openapi)

from meeshkan.nlp.schema_normalizer.schema_relations.schema_distance import (
    calc_distance,
)


def split_schema(schema):
    res = []
    split_schema_rec(schema, res, ("root",))
    return res


def split_schema_rec(schema, res, spec_path):
    if "type" in schema:
        if schema["type"] == "object":
            res.append((spec_path, schema, set(schema["properties"].keys())))
            for prop_name, prop in schema["properties"].items():
                split_schema_rec(prop, res, spec_path + ("properties", prop_name))
        elif schema["type"] == "array":
            split_schema_rec(schema["items"], res, spec_path + ("items",))


@dataclass(frozen=True, eq=True)
class SpecPart:
    path: str
    method: str
    request: bool
    code: typing.Optional[str] = None

@dataclass(frozen=True, eq=True)
class DataPath(SpecPart):
    path: typing.Any


def to_path(path_tuple):
    res = []
    for e in path_tuple:
        if e == "root":
            res.append("$")
        elif e == "properties":
            res.append(".")
        elif e == "items":
            res.append("[*]")
        else:
            res.append(e)
    return "".join(res)


class EntityNormalizer:
    allowed_methods = ["get", "post", "put"]
    props_threshold = 3
    score_threshold = 0.7

    def __init__(self, ):
        pass

    def nearest_path(self, specs: OpenAPIObject):
        """Using NLP word embeddings the function will check the responses of different
        paths and returns the list of pair of paths tuple which are having the
        cosine distance less than a pre-defined threshold = 0.1

        Arguments:
            specs {OpenAPIObject} -- OpenAPI specification
        Returns:
                List -- List of tuple pairs which are having responses very near to each other
        """
        specs_dict = convert_from_openapi(specs)
        paths_tuple_list = calc_distance(specs_dict)
        return paths_tuple_list

    # def normalize(
    #     self, specs: OpenAPIObject, path_tuple: Tuple, entity_name: str
    # ) -> OpenAPIObject:
    #     """Builds the #ref components in an OpenAPI object by understanding similar nested
    #     sructures for a set of paths.
    #
    #     Arguments:
    #         specs {OpenAPIObject} -- The open API specification object
    #         path_tuple {tuple} -- two different paths which have similar entity
    #         entity_name {str} -- an derived entity name for the similar paths
    #
    #
    #     Returns:
    #         OpenAPIObject -- Old or updated schema if #ref is created
    #     """
    #     specs_dict = convert_from_openapi(specs)
    #     is_updated, updated_specs = self._check_and_create_ref(
    #         specs_dict, path_tuple, entity_name
    #     )
    #
    #     if is_updated:
    #         return convert_to_openapi(updated_specs)
    #     else:
    #         return specs

    def normalize(
            self, spec: OpenAPIObject, path_tuple: Tuple, entity_name: str
    ) -> (typing.Sequence[DataPath], OpenAPIObject):
        """Builds the #ref components in an OpenAPI object by understanding similar nested
        sructures for a set of paths.

        Arguments:
            spec {OpenAPIObject} -- The open API specification object
            path_tuple {tuple} -- two different paths which have similar entity
            entity_name {str} -- an derived entity name for the similar paths


        Returns:
            OpenAPIObject -- Old or updated schema if #ref is created
        """
        spec_dict = convert_from_openapi(spec)
        schemas = self._extract_schemas(spec_dict, path_tuple)
        best_match = self._find_best_match(schemas)
        merged_schema = self._merge_schemas(best_match)
        spec_dict = self._add_entity(spec_dict, entity_name, merged_schema)
        spec_dict = self._replace_refs(spec_dict, best_match, entity_name)
        datapaths = [DataPath(**match[0].asdict(), path=to_path(match[1])) for match in best_match]
        return datapaths, convert_to_openapi(spec_dict)

    def _extract_schemas(self, spec, path_tuple):
        res = {}
        for path in path_tuple:
            for method_name in self.allowed_methods:
                method = spec["paths"][path].get(method_name)
                if method is not None:
                    request_schema = self._get_request_schema(method)
                    if request_schema is not None:
                        res[
                            SpecPart(path=path, method=method_name, request=True)
                        ] = self._get_schemas(request_schema)

                    for code, response in method["responses"].items():
                        response_schema = self._get_response_schema(response)
                        if response is not None:
                            res[
                                SpecPart(
                                    path=path,
                                    method=method_name,
                                    request=False,
                                    code=code,
                                )
                            ] = self._get_schemas(response_schema)

        return res

    def _get_request_schema(self, method):
        return method.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")

    def _get_response_schema(self, response):
        return response.get("content", {}).get("application/json", {}).get("schema")

    def _get_schemas(self, schema):
        schema = convert_from_openapi(schema)
        return [
            (path, spec, props)
            for path, spec, props in split_schema(schema)
            if len(props) >= self.props_threshold
        ]

    def _find_best_match(self, schemas):
        http_parts = list(schemas.keys())
        schemas = list(schemas.values())

        best_match = None
        best_match_score: typing.Optional[float] = None

        for i, match in enumerate(itertools.product(*schemas)):
            score = self._calculate_score(match)
            if best_match_score is None or score > best_match_score:
                best_match_score = score
                best_match = match

        return list(zip(http_parts, [match[0] for match in best_match], [match[1] for match in best_match]))

    def _calculate_score(self, match):
        total_score = 0.0
        total_scores = 0
        for a, b in itertools.combinations(match, r=2):
            total_score += self._pairwise_distance(a, b)
            total_scores += 1
        avg = total_score/total_scores
        if avg < self.score_threshold:
            return 0
        return avg

    def _merge_schemas(self, best_match):
        return best_match[0][2]

    def _replace_refs(self, spec_dict, best_match, entity_name):
        ref_path = f"#/components/schemas/{entity_name}"
        for match in best_match:
            spec_dict = self._replace_ref(spec_dict, match[0], match[1], ref_path)

        return spec_dict

    def _add_entity(self, spec_dict, entity_name, merged_schema):
        if "components" not in spec_dict:
            spec_dict["components"] = {}

        if "schemas" not in spec_dict["components"]:
            spec_dict["components"]["schemas"] = {}

        spec_dict["components"]["schemas"][entity_name] = merged_schema

        return spec_dict

    def _replace_ref(self, spec_dict, spec_part: SpecPart, location, ref):
        path = spec_dict["paths"][spec_part.path][spec_part.method]
        if spec_part.request:
            content = path["requestBody"]["content"]["application/json"]
        else:
            content = path["responses"][spec_part.code]["content"]["application/json"]

        content["schema"] = self._replace_ref_schema(content["schema"], location, ref)

        return spec_dict


    def _replace_ref_schema(self, top_schema, location, ref):
        schema = top_schema
        for idx in range(1, len(location) - 1):
            schema = schema[location[idx]]

        key = location[-1]

        if key == "root":
            return {"$ref": ref}
        else:
            if schema[key]["type"] == "array":
                schema[key]["items"] = {"$ref": ref}
            else:
                schema[key] = {"$ref": ref}
            return top_schema

    def _pairwise_distance(self, a, b):
        a_set = a[2]
        b_set = b[2]
        intersection = len(a_set.intersection(b_set))
        if intersection == 0:
            return 0


        a_b_diff = len(a_set - b_set)
        b_a_diff = len(b_set - a_set)

        return max(0, 1 - (a_b_diff/intersection+b_a_diff/intersection)/2)
