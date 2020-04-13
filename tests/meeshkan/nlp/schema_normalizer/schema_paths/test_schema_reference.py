import json
import os

import pytest

from meeshkan.nlp.schema_normalizer.schema_paths.schema_reference import (
    create_ref_obj,
    create_ref_path,
    create_replaced_ref,
    generate_component_dict,
    generate_replaced_ref,
)
from openapi_typed_2 import convert_from_openapi


pytestmark = pytest.mark.skip()


@pytest.fixture()
def path_tuple():
    return ("/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts")


@pytest.fixture()
def entity_name():
    return "account"


@pytest.fixture()
def best_tuple():
    return ("$schema", "accounts@array")


@pytest.fixture()
def all_paths_dict(entity_name, best_tuple, path_tuple, opbank_spec):
    opbank_spec = convert_from_openapi(opbank_spec)

    all_paths_dict = {key: [] for key in path_tuple}
    methods = ["get", "post"]
    for path in path_tuple:
        for method in opbank_spec["paths"][path].keys():
            if method in methods:
                schema = opbank_spec["paths"][path][method]["responses"]["200"][
                    "content"
                ]["application/json"]["schema"]
                all_paths_dict[path].append({method: schema})
                break  # To ensure that only single method is picked for any endpoint

    return all_paths_dict


def test_create_ref_path():
    assert create_ref_path("account") == "#/components/schemas/account"


def test_generate_component_dict():
    component_name = "account"
    init_obj = {
        "name": "nakul",
    }
    transformed_obj = {"components": {"schemas": {component_name: init_obj}}}

    assert generate_component_dict(init_obj, component_name) == transformed_obj


def test_create_ref_obj(all_paths_dict, path_tuple, best_tuple, entity_name):
    result = {
        "components": {
            "schemas": {
                "account": {
                    "required": [
                        "_links",
                        "accountId",
                        "balance",
                        "currency",
                        "identifier",
                        "identifierScheme",
                        "name",
                        "nickname",
                        "servicerIdentifier",
                        "servicerScheme",
                    ],
                    "properties": {
                        "accountId": {"type": "string"},
                        "identifier": {"type": "string"},
                        "identifierScheme": {"type": "string"},
                        "nickname": {"type": "string"},
                        "name": {"type": "string"},
                        "balance": {"type": "number"},
                        "currency": {"type": "string"},
                        "servicerScheme": {"type": "string"},
                        "servicerIdentifier": {"type": "string"},
                        "_links": {
                            "required": ["self", "transactions"],
                            "properties": {
                                "self": {
                                    "required": ["href"],
                                    "properties": {"href": {"type": "string"}},
                                    "type": "object",
                                },
                                "transactions": {
                                    "required": ["href"],
                                    "properties": {"href": {"type": "string"}},
                                    "type": "object",
                                },
                            },
                            "type": "object",
                        },
                    },
                    "type": "object",
                }
            }
        }
    }

    assert create_ref_obj(all_paths_dict, path_tuple, best_tuple, entity_name) == result


def test_generate_replaced_ref(all_paths_dict, path_tuple):
    result = {
        "required": ["_links", "accounts"],
        "properties": {
            "accounts": {"$ref": "#/components/schemas/account"},
            "_links": {
                "required": ["self"],
                "properties": {
                    "self": {
                        "required": ["href"],
                        "properties": {"href": {"type": "string"}},
                        "type": "object",
                    }
                },
                "type": "object",
            },
        },
        "type": "object",
        "$schema": "root",
    }

    specs = all_paths_dict[path_tuple[1]][0]["get"]
    specs_copy = specs.copy()
    specs_copy["$schema"] = "root"
    assert (
        generate_replaced_ref(
            specs_copy, "accounts@array", "#/components/schemas/account"
        )
        == result
    )


def test_create_replaced_ref(all_paths_dict, best_tuple, path_tuple):
    expected = {
        "/accounts/v3/accounts/{lrikubto}": {"$ref": "#/components/schemas/account"},
        "/accounts/v3/accounts": {
            "required": ["_links", "accounts"],
            "properties": {
                "accounts": {"$ref": "#/components/schemas/account"},
                "_links": {
                    "required": ["self"],
                    "properties": {
                        "self": {
                            "required": ["href"],
                            "properties": {"href": {"type": "string"}},
                            "type": "object",
                        }
                    },
                    "type": "object",
                },
            },
            "type": "object",
        },
    }

    res = create_replaced_ref(
        all_paths_dict, path_tuple, best_tuple, "" "#/components/schemas/account"
    )
    assert expected == res
