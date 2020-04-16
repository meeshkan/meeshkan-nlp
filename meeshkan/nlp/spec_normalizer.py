import itertools
import typing
from dataclasses import asdict

from meeshkan.nlp.schema_merger import SchemaMerger
from meeshkan.nlp.schema_similarity.fields_similarity import FieldsIOUSimilariaty
from openapi_typed_2 import convert_from_openapi, dataclass


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
    schema_path: typing.Any = "$"


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


class SpecNormalizer:
    allowed_methods = ["get", "post", "put"]
    props_threshold = 3

    def __init__(self,):
        self._schema_similarity = FieldsIOUSimilariaty()
        self._schema_merger = SchemaMerger()

    def normalize(
        self, spec: typing.Dict, entity_config: typing.Dict[str, typing.Sequence]
    ) -> typing.Tuple[typing.Sequence[DataPath], typing.Dict]:
        """Builds the #ref components in an OpenAPI object by understanding similar nested
        sructures for a set of paths.
        """
        datapaths: typing.List[DataPath] = []

        for entity_name, paths in entity_config.items():
            entity_datapaths, spec = self._replace_entity(spec, entity_name, paths)
            datapaths.extend(entity_datapaths)

        return datapaths, spec

    def _replace_entity(
        self, spec_dict: typing.Any, entity_name: str, paths: typing.Sequence
    ) -> typing.Tuple[typing.Sequence[DataPath], typing.Any]:
        schemas = self._extract_schemas(spec_dict, paths)
        best_match = self._find_best_match(schemas)
        if best_match is not None:
            merged_schema = self._merge_schemas(best_match)
            spec_dict = self._add_entity(spec_dict, entity_name, merged_schema)
            spec_dict = self._replace_refs(spec_dict, best_match, entity_name)
            spec_dict = self._add_x(spec_dict, entity_name, paths)
            datapaths = [
                DataPath(schema_path=to_path(match[1]), **asdict(match[0]))  # type: ignore
                for match in best_match
            ]
            return datapaths, spec_dict
        else:
            return [], spec_dict

    def _extract_schemas(self, spec, path_tuple):
        res = {}
        for path in path_tuple:
            for method_name in self.allowed_methods:
                method = spec["paths"][path].get(method_name)
                if method is not None:
                    request_schema = self._get_request_schema(method)
                    if request_schema is not None:
                        res[
                            SpecPart(path=path, method=method_name, request=True)  # type: ignore
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
                                )  # type: ignore
                            ] = self._get_schemas(response_schema)

        return res

    def _get_request_schema(self, method):
        return (
            method.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )

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
            score = self._schema_similarity.group_similarity((m[2] for m in match))
            if best_match_score is None or score > best_match_score:
                best_match_score = score
                best_match = match

        if best_match is not None:
            return list(
                zip(
                    http_parts,
                    [match[0] for match in best_match],
                    [match[1] for match in best_match],
                )
            )
        else:
            return None

    def _merge_schemas(self, matchs):
        return self._schema_merger.merge((match[2] for match in matchs))

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

    def _add_x(self, spec, entity_name, paths):
        for path in paths:
            spec["paths"][path]["x-meeshkan-entity"] = entity_name

        return spec
