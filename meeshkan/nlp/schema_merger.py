import itertools
import typing
from functools import reduce


class SchemaMerger:
    def __init__(self):
        pass

    def merge(self, schemas: typing.Iterable[typing.Any]):
        return reduce(self._merge, schemas)

    def _merge(self, a: typing.Any, b: typing.Any) -> typing.Any:
        if "$ref" in a or "$ref" in b:
            if a.get("$ref") == b.get("$ref"):
                return a
            else:
                return {"anyOf": [a, b]}
        elif "anyOf" in a and "anyOf" in b:
            return self._merge_any_of(a["anyOf"], b["anyOf"])
        elif "anyOf" in a:
            return self._merge_any_of(a["anyOf"], [b])
        elif "anyOf" in b:
            return self._merge_any_of(b["anyOf"], [a])
        elif a["type"] == "object" and b["type"] == "object":
            a_props = set(a["properties"].keys())
            b_props = set(b["properties"].keys())

            return {
                "type": "object",
                "required": list(set(a["required"]).intersection(set(b["required"]))),
                "properties": dict(
                    itertools.chain(
                        (
                            (
                                prop,
                                self._merge(
                                    a["properties"][prop], b["properties"][prop]
                                ),
                            )
                            for prop in a_props.intersection(b_props)
                        ),
                        ((prop, a["properties"][prop]) for prop in a_props - b_props),
                        ((prop, b["properties"][prop]) for prop in b_props - a_props),
                    )
                ),
            }

        elif a["type"] == "array" and b["type"] == "array":
            return {"type": "array", "items": self._merge(a["items"], b["items"])}
        elif a["type"] == b["type"]:
            return a
        else:
            return {"anyOf": [a, b]}

    def _merge_any_of(self, a, b):
        res = a
        for b_item in b:
            if b_item.get("type") == "object":
                res.append(b_item)
            elif b_item.get("type") == "array":
                merged = False
                for idx, a_item in enumerate(res):
                    if a_item.get("type") == "array":
                        res[idx] = self._merge(a_item, b_item)
                        merged = True

                if not merged:
                    res.append(b_item)
            else:
                merged = False

                for idx, a_item in enumerate(a):
                    if a_item.get("type") == b_item.get("type"):
                        merged = True

                if not merged:
                    res.append(b_item)

        return {"anyOf": res}
