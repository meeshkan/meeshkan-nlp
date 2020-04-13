import typing


class SchemaMerger:

    def merge(self, schemas: typing.Iterable[typing.Any]) -> typing.Any:
        """
        :param schemas: Iterable of schemas dicts. It will be Generator in real life.
        :return:  merged schema dict
        """
        return next(schemas)
