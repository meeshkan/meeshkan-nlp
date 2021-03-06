def test_opbank(transformer, opbank_spec, opbank_recordings):
    res = transformer.optimize_spec(opbank_spec, opbank_recordings)

    assert len(res.components.schemas["account"].properties) == 10

    assert res.components.schemas["account"]._x["x-meeshkan-id-path"] == "accountId"
    assert res.components.schemas["payment"]._x["x-meeshkan-id-path"] == "paymentId"

    assert 18 == len(res._x["x-meeshkan-data"]["account"])
    assert 1 == len(res._x["x-meeshkan-data"]["payment"])

    assert (
        "upsert" == res.paths["/v1/payments/{luawmujp}"].post._x["x-meeshkan-operation"]
    )
    assert "read" == res.paths["/accounts/v3/accounts"].get._x["x-meeshkan-operation"]
    assert (
        "random"
        == res.paths["/accounts/v3/accounts/{id}"]
        .parameters[0]
        ._x["x-meeshkan-id-type"]
    )

    assert (
        "read" == res.paths["/accounts/v3/accounts/{id}"].get._x["x-meeshkan-operation"]
    )

    assert "payment" == res.paths["/v1/payments/{luawmujp}"]._x["x-meeshkan-entity"]
    assert "account" == res.paths["/accounts/v3/accounts"]._x["x-meeshkan-entity"]
    assert "account" == res.paths["/accounts/v3/accounts/{id}"]._x["x-meeshkan-entity"]
