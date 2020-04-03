import json

import pytest
from openapi_typed_2 import convert_to_openapi

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.path_analyzer import PathAnalyzer
from meeshkan.nlp.spec_optimizer import SpecOptimizer


@pytest.fixture()
def opbank_spec():
    with open('tests/resources/op_spec.json') as f:
        return convert_to_openapi(json.load(f))

@pytest.fixture(scope='session')
def extractor():
    return EntityExtractor()

@pytest.fixture(scope='session')
def analyzer(extractor):
    return PathAnalyzer(extractor)

@pytest.fixture(scope='session')
def optimizer(extractor, analyzer):
    return SpecOptimizer()