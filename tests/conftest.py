import json

import pytest
from http_types import HttpExchangeReader
from openapi_typed_2 import convert_to_openapi, convert_from_openapi

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.entity_normalizer import EntityNormalizer
from meeshkan.nlp.path_analyzer import PathAnalyzer
from meeshkan.nlp.spec_optimizer import SpecOptimizer


@pytest.fixture()
def opbank_spec():
    with open('tests/resources/op_spec.json') as f:
        return convert_to_openapi(json.load(f))


@pytest.fixture()
def opbank_recordings():
    with open('tests/resources/op_recordings.jsonl') as f:
        return list(HttpExchangeReader.from_jsonl(f))


@pytest.fixture(scope='session')
def extractor():
    return EntityExtractor()


@pytest.fixture(scope='session')
def analyzer(extractor):
    return PathAnalyzer(extractor)

@pytest.fixture(scope='session')
def normalizer():
    return EntityNormalizer()

@pytest.fixture(scope='session')
def optimizer(extractor, analyzer, normalizer):
    return SpecOptimizer(extractor, analyzer, normalizer)

@pytest.fixture()
def accounts_schema(opbank_spec):
    spec_dict= convert_from_openapi(opbank_spec)
    path_tuple = (
            '/accounts/v3/accounts/{lrikubto}',
            '/accounts/v3/accounts')
    specs1 = spec_dict['paths'][path_tuple[0]]['get']['responses']['200']['content']['application/json']['schema']

    # we need to have a key '$schema' with any value in the root for functions to work
    specs1['$schema'] = 'root'
    return specs1
