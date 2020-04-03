from meeshkan.nlp.spec_optimizer import SpecOptimizer


def test_optimizer(optimizer, opbank_spec):
    res = optimizer.optimize_spec(opbank_spec)

    assert "accountId" == res.components.schemas["account"]._x["x-meeshkan-id-path"]
    assert "paymentId" == res.components.schemas["payment"]._x["x-meeshkan-id-path"]

    assert 5 == len(res._x["x-meeshkan-data"]["account"])
    assert 1 == len(res._x["x-meeshkan-data"]["payment"])

    assert "upsert" == res.paths["/v1/payments/{trnopysd}"].post._x["x-meeshkan-operation"]
    assert "read" == res.paths["/accounts/v3/accounts"].post._x["x-meeshkan-operation"]

    assert "payment" == res.paths["/v1/payments/{trnopysd}"]._x["x-meeshkan-entity"]
    assert "account" == res.paths["/accounts/v3/accounts"]._x["x-meeshkan-entity"]