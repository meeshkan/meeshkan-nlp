import json

from http_types import HttpExchangeBuilder

from meeshkan_nlp.data_extractor import DataExtractor
from meeshkan_nlp.spec_normalizer import DataPath


def test_group_records():
    spec = {
        "paths": {"/v1/payment/{abc}": {}, "/v1/account/{abc}/transaction/{dfe}": {}}
    }
    exchange = (
        {
            "request": {
                "method": "post",
                "host": "api.com",
                "pathname": "/v1/payment/my_id111",
                "body": json.dumps({"foo": "hello", "bar": "bye", "zaz": "baz"}),
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps({"message": "hello"}),
                "headers": {},
            },
        },
        {
            "request": {
                "method": "post",
                "host": "api.com",
                "pathname": "/v1/payment/my_id22",
                "body": json.dumps({"foo": "hello", "bar": "bye", "zaz": "baz"}),
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps({"message": "hello"}),
                "headers": {},
            },
        },
        {
            "request": {
                "method": "post",
                "host": "api.com",
                "pathname": "/v1/account/my_id444/transaction/my_id555",
                "body": json.dumps({"foo": "hello", "bar": "bye", "zaz": "baz"}),
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps({"message": "hello"}),
                "headers": {},
            },
        },
    )

    exchange = [HttpExchangeBuilder.from_dict(x) for x in exchange]

    data_extractor = DataExtractor()
    actual = data_extractor.group_records(spec, exchange)

    assert len(actual) == 2
    assert {"abc": ["my_id111", "my_id22"]} == actual[
        "/v1/payment/{abc}"
    ].path_arg_values
    assert {"abc": ["my_id444"], "dfe": ["my_id555"]} == actual[
        "/v1/account/{abc}/transaction/{dfe}"
    ].path_arg_values

    assert ("abc",) == actual["/v1/payment/{abc}"].path_args
    assert ("abc", "dfe") == actual["/v1/account/{abc}/transaction/{dfe}"].path_args

    assert len(actual["/v1/payment/{abc}"].records) == 2
    assert len(actual["/v1/account/{abc}/transaction/{dfe}"].records) == 1


def test_extract_data():
    spec = {
        "paths": {"/v1/payment/{abc}": {}, "/v1/account/{abc}/transaction/{dfe}": {}}
    }
    exchange = (
        {
            "request": {
                "method": "post",
                "host": "api.com",
                "pathname": "/v1/payment/my_id111",
                "body": json.dumps({"message": "hello", "bar": "bye", "zaz": "baz"}),
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "result": {
                            "created": {
                                "mId": "fds5f4-5f",
                                "message": "hello",
                                "bar": "bye",
                                "zaz": "baz",
                            }
                        }
                    }
                ),
                "headers": {},
            },
        },
        {
            "request": {
                "method": "put",
                "host": "api.com",
                "pathname": "/v1/payment/my_id22",
                "body": json.dumps(
                    {"mId": "fds5f4-5f", "foo": "hello", "bar": "bye", "zaz": "baz"}
                ),
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "result": {
                            "updated": {
                                "mId": "fds5f4-5f",
                                "foo": "hello",
                                "bar": "bye",
                                "zaz": "baz",
                            }
                        }
                    }
                ),
                "headers": {},
            },
        },
        {
            "request": {
                "method": "get",
                "host": "api.com",
                "pathname": "/v1/account/my_id444/transaction/my_id555",
                "body": "",
                "query": {},
                "protocol": "http",
                "headers": {},
            },
            "response": {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "results": [
                            {
                                "mId": "fds5f4-5f",
                                "foo": "hello",
                                "bar": "bye",
                                "zaz": "baz",
                            },
                            {
                                "mId": "fsdfre-5f",
                                "foo": "bye",
                                "bar": "hello",
                                "zaz": "baz",
                            },
                        ]
                    }
                ),
                "headers": {},
            },
        },
    )

    exchange = [HttpExchangeBuilder.from_dict(x) for x in exchange]

    data_extractor = DataExtractor()
    grouped_records = data_extractor.group_records(spec, exchange)

    datapaths = {
        "payment": [
            DataPath(
                path="/v1/payment/{abc}", method="post", request=True, schema_path="$"
            ),
            DataPath(
                path="/v1/payment/{abc}",
                method="post",
                request=False,
                code="200",
                schema_path="$.result.created",
            ),
            DataPath(
                path="/v1/payment/{abc}",
                method="put",
                request=False,
                code="200",
                schema_path="$.result.updated",
            ),
            DataPath(
                path="/v1/payment/{abc}", method="put", request=True, schema_path="$"
            ),
        ],
        "transaction": [
            DataPath(
                path="/v1/account/{abc}/transaction/{dfe}",
                method="get",
                request=False,
                code="200",
                schema_path="$.results[*]",
            )
        ],
    }

    actual = data_extractor.extract_data(datapaths, grouped_records)

    assert len(actual) == 2
    assert len(actual["payment"]) == 4
    assert len(actual["transaction"]) == 2
