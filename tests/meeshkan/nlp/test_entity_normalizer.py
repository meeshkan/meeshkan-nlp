import copy
import json
import os

from openapi_typed_2 import (
    convert_to_openapi,
    convert_to_OpenAPIObject,
    convert_from_openapi,
)

from meeshkan.nlp.entity_normalizer import EntityNormalizer
from tests.utils import spec_dict, add_item


def test_entity_normalizer_opbank():
    opbank_original_filepath = os.path.abspath("tests/resources/op_spec.json")
    opbank_components_filepath = os.path.abspath(
        "tests/resources/op_component_spec.json"
    )
    with open(opbank_original_filepath, encoding="utf8") as f:
        data = json.load(f)
        org_specs = convert_to_openapi(data)

    with open(opbank_components_filepath, encoding="utf8") as f:
        comp_specs = json.load(f)

    path_tuple = ("/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts")

    entity_name = "account"
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(org_specs, path_tuple, entity_name)
    print(updated_specs)
    # assert convert_from_openapi((updated_specs)) == comp_specs


def test_entity_normalizer_responses():
    payment_spec = {
        "type": "object",
        "required": ["valueDate", "receiverBic"],
        "properties": {
            "amount": {"type": "integer"},
            "subject": {"type": "string"},
            "currency": {"type": "string"},
            "payerIban": {"type": "string"},
            "valueDate": {"type": "string"},
            "receiverBic": {"type": "string"},
            "receiverIban": {"type": "string"},
            "receiverName": {"type": "string"},
            "paymentId": {"type": "string"},
        },
    }

    schema_single = {
        "type": "object",
        "required": [],
        "properties": {
            "result": {

                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "field": {"type": "integer"},
                            "another_field": {"type": "string"},
                            "comment": {"type": "string"},
                            "whatever": {"type": "string"},

                        },
                    },
                    "payment": payment_spec,
                    "password": {"type": "string"},
                    "date": {"type": "datetime"},
                },
            },
        },
    }

    schema_array = {
        "type": "object",
        "required": [],
        "properties": {
            "results": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "page_number": {"type": "integer"},
                            "more_results": {"type": "string"},
                            "password": {"type": "string"},
                            "date": {"type": "datetime"},
                        },
                    },
                    "payments": {"items": payment_spec, "type": "array"},
                    "comment": {"type": "string"},
                    "whatever": {"type": "string"},
                },
            },
        },
    }

    spec = spec_dict(
        path="/payments/{id}", response_schema=schema_single, method="get",
    )
    add_item(
        spec, path="/payments", response_schema=schema_array, method="get",
    )
    spec = convert_to_OpenAPIObject(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

    assert payment_spec == convert_from_openapi(
        updated_specs.components.schemas["payment"]
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["results"]
        .properties["payments"]
        .items._ref
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments/{id}"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["result"]
        .properties["payment"]
        ._ref
    )


def test_entity_normalizer_responses_types():
    payment_spec = {
        "type": "object",
        "required": ["valueDate", "receiverBic"],
        "properties": {
            "amount": {"type": "float"},
            "subject": {"type": "string"},
            "currency": {"type": "string"},
            "payerIban": {"type": "string"},
            "valueDate": {"type": "datetime"},
            "receiverBic": {"type": "string"},
            "receiverIban": {"type": "string"},
            "receiverName": {"type": "string"},
            "paymentId": {"type": "string"},
        },
    }

    schema_single = {
        "type": "object",
        "required": [],
        "properties": {
            "result": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "field": {"type": "integer"},
                            "another_field": {"type": "string"},
                        },
                    },
                    "payment": payment_spec,
                },
            },
        },
    }

    schema_array = {
        "type": "object",
        "required": [],
        "properties": {
            "results": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "page_number": {"type": "integer"},
                            "more_results": {"type": "string"},
                        },
                    },
                    "payments": {"items": payment_spec, "type": "array"},
                },
            },
        },
    }

    spec = spec_dict(
        path="/payments/{id}", response_schema=schema_single, method="get",
    )
    add_item(
        spec, path="/payments", response_schema=schema_array, method="get",
    )
    spec = convert_to_OpenAPIObject(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

    assert payment_spec == convert_from_openapi(
        updated_specs.components.schemas["payment"]
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["results"]
        .properties["payments"]
        .items._ref
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments/{id}"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["result"]
        .properties["payment"]
        ._ref
    )


def test_entity_normalizer_responses_optional():
    payment_spec = {
        "type": "object",
        "required": ["valueDate", "receiverBic"],
        "properties": {
            "amount": {"type": "integer"},
            "subject": {"type": "string"},
            "currency": {"type": "string"},
            "payerIban": {"type": "string"},
            "valueDate": {"type": "string"},
            "receiverBic": {"type": "string"},
            "receiverIban": {"type": "string"},
            "receiverName": {"type": "string"},
            "paymentId": {"type": "string"},
        },
    }

    payment_spec_single = copy.deepcopy(payment_spec)
    payment_spec_single["properties"]["message"] = {"type": "string"}
    payment_spec_single["properties"]["details"] = {"type": "string"}
    schema_single = {
        "type": "object",
        "required": [],
        "properties": {
            "result": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "field": {"type": "integer"},
                            "another_field": {"type": "string"},
                        },
                    },
                    "payment": payment_spec_single,
                },
            },
        },
    }

    schema_array = {
        "type": "object",
        "required": [],
        "properties": {
            "results": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "page_number": {"type": "integer"},
                            "more_results": {"type": "string"},
                        },
                    },
                    "payments": {"items": payment_spec, "type": "array"},
                },
            },
        },
    }

    spec = spec_dict(
        path="/payments/{id}", response_schema=schema_single, method="get",
    )
    add_item(
        spec, path="/payments", response_schema=schema_array, method="get",
    )
    spec = convert_to_OpenAPIObject(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

    assert payment_spec_single == convert_from_openapi(
        updated_specs.components.schemas["payment"]
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["results"]
        .properties["payments"]
        .items._ref
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments/{id}"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["result"]
        .properties["payment"]
        ._ref
    )


def test_entity_normalizer_request_response():
    payment_spec = {
        "type": "object",
        "required": ["valueDate", "receiverBic"],
        "properties": {
            "amount": {"type": "integer"},
            "subject": {"type": "string"},
            "currency": {"type": "string"},
            "payerIban": {"type": "string"},
            "valueDate": {"type": "string"},
            "receiverBic": {"type": "string"},
            "receiverIban": {"type": "string"},
            "receiverName": {"type": "string"},
            "paymentId": {"type": "string"},
        },
    }

    payment_spec_single = copy.deepcopy(payment_spec)
    payment_spec_single["properties"]["message"] = {"type": "string"}
    payment_spec_single["properties"]["details"] = {"type": "string"}
    schema_single = {
        "type": "object",
        "required": [],
        "properties": {
            "result": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "field": {"type": "integer"},
                            "another_field": {"type": "string"},
                        },
                    },
                    "payment": payment_spec_single,
                },
            },
        },
    }

    schema_single_request = copy.deepcopy(payment_spec)
    del schema_single_request["properties"]["paymentId"]

    schema_array = {
        "type": "object",
        "required": [],
        "properties": {
            "results": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": ["valueDate", "receiverBic"],
                        "properties": {
                            "page_number": {"type": "integer"},
                            "more_results": {"type": "string"},
                        },
                    },
                    "payments": {"items": payment_spec, "type": "array"},
                },
            },
        },
    }

    spec = spec_dict(
        path="/payments/{id}", response_schema=schema_single, method="get",
    )
    add_item(
        spec, path="/payments", response_schema=schema_array, method="get",
    )

    add_item(
        spec,
        path="/payments",
        request_schema=schema_single_request,
        response_schema=schema_single,
        method="post",
    )

    spec = convert_to_OpenAPIObject(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

    assert payment_spec_single == convert_from_openapi(
        updated_specs.components.schemas["payment"]
    )
    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["results"]
        .properties["payments"]
        .items._ref
    )

    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .post.responses["200"]
        .content["application/json"]
        .schema.properties["result"]
        .properties["payment"]._ref
    )

    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments"]
        .post.requestBody.content["application/json"]
        .schema._ref
    )

    assert (
        "#/components/schemas/payment"
        == updated_specs.paths["/payments/{id}"]
        .get.responses["200"]
        .content["application/json"]
        .schema.properties["result"]
        .properties["payment"]
        ._ref
    )
