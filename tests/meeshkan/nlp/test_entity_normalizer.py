import os
from meeshkan.nlp.entity_normalizer import EntityNormalizer
from openapi_typed_2 import convert_to_openapi, convert_from_openapi
import json


def test_entity_normalizer():
    opbank_original_filepath = os.path.abspath('../../resources/op_spec.json')
    opbank_components_filepath = os.path.abspath('../../resources/op_component_spec.json')
    with open(opbank_original_filepath, encoding='utf8') as f:
        data = json.load(f)
        org_specs = convert_to_openapi(data)

    with open(opbank_components_filepath, encoding='utf8') as f:
        comp_specs = json.load(f)


    path_tuple = (
        '/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw',
        '/accounts/v3/accounts')

    entity_name = 'account'
    entity_normalizer = EntityNormalizer()
    updated_specs = entity_normalizer.normalize(org_specs, path_tuple, entity_name)
    # assert convert_from_openapi((updated_specs)) == comp_specs
