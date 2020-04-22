import typing
from collections import defaultdict
from dataclasses import dataclass

from http_types import HttpExchange
from jsonpath_rw import parse

from meeshkan_nlp.ids.paths import path_to_regex
from meeshkan_nlp.spec_normalizer import DataPath


@dataclass(frozen=True)
class PathRecords:
    path_args: typing.Tuple[str]
    path_arg_values: typing.Dict[str, typing.List[str]]
    records: typing.List[HttpExchange]


class DataExtractor:
    def __init__(self):
        pass

    def group_records(
        self, spec: typing.Dict, recordings: typing.List[HttpExchange]
    ) -> typing.Dict[str, PathRecords]:
        path_regexs = [
            (pathname, *path_to_regex(pathname)) for pathname in spec["paths"].keys()
        ]

        res = {
            pathname: PathRecords(
                path_arg_values={param_name: [] for param_name in parameter_names},
                records=list(),
                path_args=parameter_names,
            )
            for pathname, path_regex, parameter_names in path_regexs
        }

        for rec in recordings:
            for pathname, path_regex, parameter_names in path_regexs:
                values = self._match_to_path(path_regex, rec.request.pathname)
                if values is not None:
                    res[pathname].records.append(rec)
                    for name, value in zip(parameter_names, values):
                        res[pathname].path_arg_values[name].append(value)
                    break

        return res

    def extract_data(
        self,
        datapaths: typing.Dict[str, typing.Iterable[DataPath]],
        grouped_records: typing.Dict[str, PathRecords],
    ) -> typing.Mapping[str, typing.Any]:
        entity_values = defaultdict(list)
        for pathname, records in grouped_records.items():
            for record in records.records:
                entity, values = self._match_entity(pathname, record, datapaths)
                if entity is not None:
                    entity_values[entity].extend(values)

        return entity_values

    def _match_entity(
        self,
        pathname: str,
        record: HttpExchange,
        datapaths: typing.Dict[str, typing.Iterable[DataPath]],
    ):
        total_values = []
        res_entity = None
        for entity, paths in datapaths.items():
            for path in paths:
                if self._match(pathname, record, path):
                    values = self._extract_entity_values(path, record)
                    res_entity = entity
                    total_values.extend(values)

            if res_entity is not None:
                return res_entity, total_values

        return None, []

    def _match(self, pathname: str, record: HttpExchange, path: DataPath) -> bool:
        return (
            pathname == path.path
            and path.method == record.request.method.value
            and (
                path.request
                or record.response.statusCode == int(typing.cast(str, path.code))
            )
        )

    def _extract_entity_values(self, path: DataPath, record: HttpExchange):
        body = record.request.bodyAsJson if path.request else record.response.bodyAsJson
        return [f.value for f in parse(path.schema_path).find(body)]

    def _match_to_path(
        self, path_as_regex, request_path: str
    ) -> typing.Optional[typing.Mapping[str, typing.Any]]:
        match = path_as_regex.match(request_path)

        if match is None:
            return None

        captures = match.groups()
        return captures
