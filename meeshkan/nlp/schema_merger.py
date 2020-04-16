import typing
from functools import reduce


class SchemaMerger:
    def __init__(self):
        pass

    def merge(self, specs: typing.Iterable[typing.Any]):
        return reduce(self._merge, specs)

    def _merge(self, a: typing.Any, b: typing.Any) -> typing.Any:
        return a
