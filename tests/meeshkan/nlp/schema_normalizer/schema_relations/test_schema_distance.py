import os
import json
from meeshkan.nlp.schema_normalizer.schema_relations.schema_distance import calc_distance, \
    get_all_paths


opbank_original_filepath = os.path.abspath('../../../../resources/op_spec.json')
with open(opbank_original_filepath, encoding='utf8') as f:
    specs_dict = json.load(f)




def test_calc_distance():
    result = [('/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw', '/accounts/v3/accounts')]

    assert calc_distance(specs_dict) == result

def test_get_all_paths():
    result = ['/v1/payments/{trnopysd}',
              '/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw',
              '/accounts/v3/accounts']
    assert get_all_paths(specs_dict) == result
