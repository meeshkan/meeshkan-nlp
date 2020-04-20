import json

import pytest
import spacy
from http_types import HttpExchangeReader

from meeshkan.nlp.entity_extractor import EntityExtractor
from meeshkan.nlp.ids.id_classifier import IdClassifier
from meeshkan.nlp.path_analyzer import PathAnalyzer
from meeshkan.nlp.spec_normalizer import SpecNormalizer
from meeshkan.nlp.spec_transformer import SpecTransformer
from openapi_typed_2 import convert_from_openapi, convert_to_openapi
from meeshkan.nlp.schema_similarity.fields_similarity import FieldsEmbeddingsSimilariaty


@pytest.fixture(scope="session")
def nlp():
    return spacy.load("en_core_web_lg")


@pytest.fixture()
def opbank_spec():
    with open("tests/resources/op_spec.json") as f:
        return convert_to_openapi(json.load(f))


@pytest.fixture()
def opbank_recordings():
    with open("tests/resources/op_recordings.jsonl") as f:
        return list(HttpExchangeReader.from_jsonl(f))


@pytest.fixture(scope="session")
def extractor(nlp):
    return EntityExtractor(nlp)


@pytest.fixture(scope="session")
def analyzer(extractor):
    return PathAnalyzer(extractor)


@pytest.fixture(scope="session")
def normalizer():
    return SpecNormalizer()


@pytest.fixture(scope="session")
def transformer(extractor, analyzer, normalizer):
    return SpecTransformer(extractor, analyzer, normalizer, IdClassifier())


@pytest.fixture(scope="session")
def fields_embeddings_similarity(nlp):
    return FieldsEmbeddingsSimilariaty(nlp)

@pytest.fixture()
def accounts_schema(opbank_spec):
    spec_dict = convert_from_openapi(opbank_spec)
    accounts_schema = spec_dict["paths"]["/accounts/v3/accounts/{lrikubto}"]["get"][
        "responses"
    ]["200"]["content"]["application/json"]["schema"]
    return accounts_schema
