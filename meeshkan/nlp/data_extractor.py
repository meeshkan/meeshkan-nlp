import typing
from collections import defaultdict

from http_types import HttpExchange

from meeshkan.nlp.spec_normalizer import DataPath


class DataExtractor:
    def __init__(self):
        pass

    def extract_data(self, datapaths: typing.Dict[str, typing.Sequence[DataPath]], grouped_records: typing.Iterable[typing.Tuple[str, typing.Iterable[HttpExchange]]]) -> typing.Mapping[str, typing.Any]:
        entity_values = defaultdict(list)
        for pathname, records in grouped_records:
            for record in records:
                entity, values = self._match_entity(pathname, record, datapaths)
                if entity is not None:
                    entity_values[entity].extend(values)

        return entity_values

    def _match_entity(self, pathname, record, datapaths):
        for entity, paths in datapaths:
            for path in paths:
                if self._match(pathname, record, path):
                    return entity, self._extract_entity_value(path, record)

        return None, None

    def _match(self, pathname, record, path):
        pass

    def _extract_entity_value(self, path, record):
        pass
