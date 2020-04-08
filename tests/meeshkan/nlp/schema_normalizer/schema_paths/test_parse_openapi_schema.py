import json
import os

from meeshkan.nlp.schema_normalizer.schema_paths.parse_openapi_schema import (
    parse_schema,
)
from openapi_typed_2 import convert_from_openapi


def test_op_parse_schema(opbank_spec):
    openapi_specs = convert_from_openapi(opbank_spec)
    path_tuple = ("/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts")
    specs1 = openapi_specs["paths"][path_tuple[0]]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]

    parsed_schema_list = [
        {
            "$schema": [
                "_links",
                "_links#self",
                "_links#self#href",
                "_links#transactions",
                "_links#transactions#href",
                "accountId",
                "balance",
                "currency",
                "identifier",
                "identifierScheme",
                "name",
                "nickname",
                "servicerIdentifier",
                "servicerScheme",
            ]
        },
        {"_links@object": ["self", "self#href", "transactions", "transactions#href"]},
        {
            "_links@object#self@object": ["href"],
            "_links@object#transactions@object": ["href"],
        },
    ]

    assert parse_schema(specs1) == parsed_schema_list
