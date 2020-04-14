from meeshkan.nlp.operation_classifier import OperationClassifier
from tests.utils import add_item, spec_dict


def test_operation_classifier():
    cl = OperationClassifier()

    schema = {
        "type": "object",
        "required": [],
        "properties": {"result": {"type": "string"}},
    }

    spec = spec_dict(path="/payments/{id}", response_schema=schema, method="get",)

    add_item(
        spec, path="/payments/{id}", response_schema=schema, method="delete",
    )

    add_item(
        spec,
        path="/payments",
        request_schema=schema,
        response_schema=None,
        method="post",
    )

    add_item(
        spec,
        path="/payments/process",
        request_schema=None,
        response_schema=schema,
        method="post",
    )

    add_item(
        spec,
        path="/payments/confirm",
        request_schema=schema,
        response_schema=schema,
        method="put",
    )

    spec = cl.fill_operations(spec)

    assert spec["paths"]["/payments/{id}"]["get"]["x-meeshkan-operation"] == "read"
    assert spec["paths"]["/payments/{id}"]["delete"]["x-meeshkan-operation"] == "delete"
    assert spec["paths"]["/payments"]["post"]["x-meeshkan-operation"] == "upsert"
    assert "x-meeshkan-operation" not in spec["paths"]["/payments/process"]["post"]
    assert spec["paths"]["/payments/confirm"]["put"]["x-meeshkan-operation"] == "upsert"
