import copy
import json
import os

from openapi_typed_2 import (
    convert_to_openapi,
    convert_from_openapi,
)

from meeshkan.nlp.entity_normalizer import EntityNormalizer
from tests.utils import spec_dict, add_item


def test_opbank(opbank_spec):
    entity_normalizer = EntityNormalizer()

    path_tuple = ("/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts")
    entity_name = "account"
    datapaths, opbank_spec = entity_normalizer.normalize(opbank_spec, path_tuple, entity_name)

    account_schema = convert_from_openapi(
        opbank_spec.components.schemas["account"]
    )
    assert "accountId" in account_schema["properties"]

    assert (
            "#/components/schemas/account"
            == opbank_spec.paths["/accounts/v3/accounts"]
            .get.responses["200"]
            .content["application/json"]
            .schema.properties["accounts"]
            .items._ref
    )
    assert (
            "#/components/schemas/account"
            == opbank_spec.paths["/accounts/v3/accounts/{lrikubto}"]
            .get.responses["200"]
            .content["application/json"]
            .schema
            ._ref
    )

    path_tuple = ("/v1/payments/{luawmujp}",)
    entity_name = "payment"
    datapaths, opbank_spec = entity_normalizer.normalize(opbank_spec, path_tuple, entity_name)

    payment_schema = convert_from_openapi(
        opbank_spec.components.schemas["payment"]
    )
    # assert "paymentId" in payment_schema["properties"]

    assert (
            "#/components/schemas/payment"
            == opbank_spec.paths["/v1/payments/{luawmujp}"]
            .post.requestBody
            .content["application/json"]
            .schema._ref
    )
    assert (
            "#/components/schemas/payment"
            == opbank_spec.paths["/v1/payments/{luawmujp}"]
            .post.responses["200"]
            .content["application/json"]
            .schema
            ._ref
    )

    assert "accountId" in account_schema["properties"]

    assert (
            "#/components/schemas/account"
            == opbank_spec.paths["/accounts/v3/accounts"]
            .get.responses["200"]
            .content["application/json"]
            .schema.properties["accounts"]
            .items._ref
    )
    assert (
            "#/components/schemas/account"
            == opbank_spec.paths["/accounts/v3/accounts/{lrikubto}"]
            .get.responses["200"]
            .content["application/json"]
            .schema
            ._ref
    )


def test_responses_exact_match():
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
    spec = convert_to_openapi(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    datapaths, updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

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


def test_responses_diff_types():
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
    spec = convert_to_openapi(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    datapaths, updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

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


def test_responses_diff_fields():
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
    spec = convert_to_openapi(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    datapaths, updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

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


def test_request_response():
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

    spec = convert_to_openapi(spec)

    path_tuple = ("/payments/{id}", "/payments")

    entity_name = "payment"
    entity_normalizer = EntityNormalizer()
    datapaths, updated_specs = entity_normalizer.normalize(spec, path_tuple, entity_name)

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
