import typing

from http_types import HttpExchange


class PathMatcher:
    def __init__(self, id_classifier):
        self._id_classifier = id_classifier

    def check_id(self, path_pattern: str, recordings: typing.Iterable[HttpExchange]):
        pass
