from meeshkan.nlp.schema_normalizer.schema_paths.schema_to_fields import (
    camel_case_split,
    parse_schema_features,
    schema_remove_types,
    split_by_all,
    split_by_level,
    split_by_type,
)


def test_split_by_type():
    obj = "accounts@array"
    assert split_by_type(obj) == ["accounts", "array"]


def test_split_by_level():
    obj = "accounts@array"
    assert split_by_level(obj) == ["accounts@array"]

    obj = "accounts@array#balance@number"
    assert split_by_level(obj) == ["accounts@array", "balance@number"]


def test_split_by_all():
    obj = "users@array#name@string"
    assert split_by_all(obj) == [["users", "array"], ["name", "string"]]


def test_parse_schema_features():
    obj = ["users@array", "users@array#name@string", "users@array#age@number"]
    assert parse_schema_features(obj) == ["users", "users", "name", "users", "age"]


def test_camel_case_split():
    obj = "isItName"
    assert camel_case_split(obj) == ["is", "It", "Name"]


def test_schema_remove_types():
    obj = "users@array#name@string"
    assert schema_remove_types(obj) == "users#name"
