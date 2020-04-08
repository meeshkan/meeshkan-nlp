import json
import os

from meeshkan.nlp.schema_normalizer.schema_relations.schema_distance import (
    calc_distance,
    get_all_paths,
)


def get_specs_dict():
    opbank_original_filepath = os.path.abspath("tests/resources/op_spec.json")
    with open(opbank_original_filepath, encoding="utf8") as f:
        specs_dict = json.load(f)
    return specs_dict


def test_calc_distance():
    result = [("/accounts/v3/accounts/{lrikubto}", "/accounts/v3/accounts")]

    assert calc_distance(get_specs_dict()) == result


def test_get_all_paths():
    result = {
        "/v1/payments/{luawmujp}",
        "/accounts/v3/accounts/{lrikubto}",
        "/accounts/v3/accounts",
    }
    assert set(get_all_paths(get_specs_dict())) == result
