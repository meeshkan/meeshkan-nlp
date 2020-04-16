from meeshkan.nlp.schema_merger import SchemaMerger
from openapi_typed_2 import convert_to_openapi, convert_to_Schema


def test_merge():
    schema1 = {
        "type": "object",
        "required": ["foo", "baz"],
        "properties": {
            "foo": {"type": "integer"},
            "bar": {"type": "string"},
            "baz": {"type": "string"},
            "faz": {
                "type": "object",
                "required": ["field1"],
                "properties": {
                    "field1": {"type": "integer"},
                    "field2": {"type": "string"},
                    "field3": {"type": "string"},
                },
            },
        },
    }

    schema2 = {
        "type": "object",
        "required": ["foo", "bar"],
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "string"},
            "zaz": {"type": "string"},
            "faz": {
                "type": "object",
                "required": ["field1", "field4"],
                "properties": {
                    "field1": {"type": "integer"},
                    "field2": {"type": "string"},
                    "field3": {"type": "string"},
                    "field4": {"type": "integer"},
                },
            },
        },
    }

    schema3 = {
        "type": "object",
        "required": ["foo", "bar"],
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "string"},
            "zaz": {"type": "string"},
            "faz": {"type": "string"},
        },
    }

    schema_merger = SchemaMerger()

    actual = schema_merger.merge((schema1, schema2, schema3))

    expected = {
        "type": "object",
        "required": ["foo"],
        "properties": {
            "foo": {"anyOf": [{"type": "integer"}, {"type": "string"}]},
            "bar": {"type": "string"},
            "baz": {"type": "string"},
            "zaz": {"type": "string"},
            "faz": {
                "anyOf": [
                    {"type": "string"},
                    {
                        "type": "object",
                        "required": ["field1"],
                        "properties": {
                            "field1": {"type": "integer"},
                            "field2": {"type": "string"},
                            "field3": {"type": "string"},
                            "field4": {"type": "integer"},
                        },
                    },
                ]
            },
        },
    }

    schema = convert_to_Schema(actual)
    assert schema is not None

    assert len(actual["properties"]) == len(expected["properties"])
    assert len(actual["required"]) == 1
    assert "foo" in actual["required"]
    assert actual["properties"]["bar"] == {"type": "string"}
    assert actual["properties"]["baz"] == {"type": "string"}
    assert actual["properties"]["zaz"] == {"type": "string"}
    assert len(actual["properties"]["foo"]["anyOf"]) == 2
    assert {"type": "integer"} in actual["properties"]["foo"]["anyOf"]
    assert {"type": "string"} in actual["properties"]["foo"]["anyOf"]
    assert {
        "type": "object",
        "required": ["field1"],
        "properties": {
            "field1": {"type": "integer"},
            "field2": {"type": "string"},
            "field3": {"type": "string"},
            "field4": {"type": "integer"},
        },
    } in actual["properties"]["faz"]["anyOf"]
