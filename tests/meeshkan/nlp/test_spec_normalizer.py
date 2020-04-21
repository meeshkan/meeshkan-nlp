import copy

from openapi_typed_2 import convert_from_openapi, convert_to_openapi

from meeshkan.nlp.spec_normalizer import DataPath, SpecNormalizer
from tests.utils import add_item, spec_dict


def test_opbank(opbank_spec):
    opbank_spec = convert_from_openapi(opbank_spec)
    spec_normalizer = SpecNormalizer()

    entity_config = {
        "account": ["/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts"],
        "payment": ["/v1/payments/{luawmujp}"],
    }

    datapaths, opbank_spec = spec_normalizer.normalize(opbank_spec, entity_config)

    opbank_spec = convert_to_openapi(opbank_spec)

    account_schema = convert_from_openapi(opbank_spec.components.schemas["account"])
    payment_schema = convert_from_openapi(opbank_spec.components.schemas["payment"])

    assert 4 == len(datapaths)
    assert (
        DataPath(
            path="/accounts/v3/accounts/{lrikubto}",
            code="200",
            request=False,
            method="get",
            schema_path="$",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/accounts/v3/accounts",
            code="200",
            request=False,
            method="get",
            schema_path="$.accounts[*]",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/v1/payments/{luawmujp}",
            code="200",
            request=False,
            method="post",
            schema_path="$",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/v1/payments/{luawmujp}", request=True, method="post", schema_path="$"
        )
        in datapaths
    )

    assert "accountId" in account_schema["properties"]
    assert "paymentId" in payment_schema["properties"]  # TODO Nikolay fix this

    assert (
        "account" == opbank_spec.paths["/accounts/v3/accounts"]._x["x-meeshkan-entity"]
    )
    assert (
        "account"
        == opbank_spec.paths["/accounts/v3/accounts/{lrikubto}"]._x["x-meeshkan-entity"]
    )
    assert (
        "payment"
        == opbank_spec.paths["/v1/payments/{luawmujp}"]._x["x-meeshkan-entity"]
    )

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
        .schema._ref
    )

    assert (
        "#/components/schemas/payment"
        == opbank_spec.paths["/v1/payments/{luawmujp}"]
        .post.requestBody.content["application/json"]
        .schema._ref
    )
    assert (
        "#/components/schemas/payment"
        == opbank_spec.paths["/v1/payments/{luawmujp}"]
        .post.responses["200"]
        .content["application/json"]
        .schema._ref
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

    entity_config = {"payment": ["/payments/{id}", "/payments"]}

    spec_normalizer = SpecNormalizer()
    datapaths, updated_specs = spec_normalizer.normalize(spec, entity_config)
    updated_specs = convert_to_openapi(updated_specs)

    assert 2 == len(datapaths)
    assert (
        DataPath(
            path="/payments",
            code="200",
            request=False,
            method="get",
            schema_path="$.results.payments[*]",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/payments/{id}",
            code="200",
            request=False,
            method="get",
            schema_path="$.result.payment",
        )
        in datapaths
    )

    actual_spec = convert_from_openapi(updated_specs.components.schemas["payment"])

    assert payment_spec["properties"] == actual_spec["properties"]
    assert set(payment_spec["required"]) == set(actual_spec["required"])

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

    entity_config = {"payment": ["/payments/{id}", "/payments"]}

    spec_normalizer = SpecNormalizer()
    datapaths, updated_specs = spec_normalizer.normalize(spec, entity_config)
    updated_specs = convert_to_openapi(updated_specs)

    assert 2 == len(datapaths)
    assert (
        DataPath(
            path="/payments",
            code="200",
            request=False,
            method="get",
            schema_path="$.results.payments[*]",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/payments/{id}",
            code="200",
            request=False,
            method="get",
            schema_path="$.result.payment",
        )
        in datapaths
    )

    actual_spec = convert_from_openapi(updated_specs.components.schemas["payment"])

    assert payment_spec["properties"] == actual_spec["properties"]
    assert set(payment_spec["required"]) == set(actual_spec["required"])

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

    entity_config = {"payment": ["/payments/{id}", "/payments"]}

    spec_normalizer = SpecNormalizer()
    datapaths, updated_specs = spec_normalizer.normalize(spec, entity_config)
    updated_specs = convert_to_openapi(updated_specs)

    assert 2 == len(datapaths)
    assert (
        DataPath(
            path="/payments",
            code="200",
            request=False,
            method="get",
            schema_path="$.results.payments[*]",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/payments/{id}",
            code="200",
            request=False,
            method="get",
            schema_path="$.result.payment",
        )
        in datapaths
    )

    actual_spec = convert_from_openapi(updated_specs.components.schemas["payment"])

    assert payment_spec_single["properties"] == actual_spec["properties"]
    assert set(payment_spec_single["required"]) == set(actual_spec["required"])

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
        response_schema=copy.deepcopy(schema_single),
        method="post",
    )

    entity_config = {"payment": ["/payments/{id}", "/payments"]}

    spec_normalizer = SpecNormalizer()
    datapaths, updated_specs = spec_normalizer.normalize(spec, entity_config)
    updated_specs = convert_to_openapi(updated_specs)

    assert 4 == len(datapaths)
    assert (
        DataPath(
            path="/payments",
            code="200",
            request=False,
            method="get",
            schema_path="$.results.payments[*]",
        )
        in datapaths
    )
    assert (
        DataPath(
            path="/payments/{id}",
            code="200",
            request=False,
            method="get",
            schema_path="$.result.payment",
        )
        in datapaths
    )
    assert (
        DataPath(path="/payments", request=True, method="post", schema_path="$")
        in datapaths
    )
    assert (
        DataPath(
            path="/payments",
            code="200",
            request=False,
            method="post",
            schema_path="$.result.payment",
        )
        in datapaths
    )

    actual_spec = convert_from_openapi(updated_specs.components.schemas["payment"])

    assert payment_spec_single["properties"] == actual_spec["properties"]
    assert set(payment_spec_single["required"]) == set(actual_spec["required"])

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
        .properties["payment"]
        ._ref
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
