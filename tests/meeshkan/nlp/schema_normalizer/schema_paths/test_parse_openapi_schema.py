import json
import os

import pytest

from meeshkan.nlp.schema_normalizer.schema_paths.parse_openapi_schema import \
    parse_schema
from openapi_typed_2 import convert_from_openapi

pytestmark = pytest.mark.skip()


def test_op_parse_schema():
    schema = {
        "type": "object",
        "required": [],
        "properties": {
            "result": {
                "type": "object",
                "required": [],
                "properties": {
                    "metadata": {
                        "type": "object",
                        "required": [],
                        "properties": {
                            "field": {"type": "integer"},
                            "another_field": {"type": "string"},
                            "comment": {"type": "string"},
                        },
                    },
                    "payment": {
                        "type": "object",
                        "required": [],
                        "properties": {
                            "paymentId": {"type": "integer"},
                            "payment_details": {"type": "string"},
                            "amount": {"type": "integer"},
                        },
                    },
                },
            },
        },
    }

    res = parse_schema(schema)

    assert 4 == len(res)
