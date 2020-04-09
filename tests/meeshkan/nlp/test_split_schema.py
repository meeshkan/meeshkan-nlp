from meeshkan.nlp.entity_normalizer import split_schema


def test_split_schema():
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

    res = split_schema(schema_array)

    assert 4 == len(res)

    assert {"results"} == res[("root",)]
    assert {"metadata", "payments"} == res[("root", "properties", "results")]
    assert {"page_number", "more_results"} == res[
        ("root", "properties", "results", "properties", "metadata")
    ]
    assert 9 == len(
        res[("root", "properties", "results", "properties", "payments", "items")]
    )
