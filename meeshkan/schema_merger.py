import typing


class SchemaMerger:
    def merge(self, schemas: typing.Iterator[typing.Any]) -> typing.Any:
        """
        :param schemas: Iterable of schemas dicts. It will be Generator in real life.
        :return:  merged schema dict
        """
        return next(schemas)
