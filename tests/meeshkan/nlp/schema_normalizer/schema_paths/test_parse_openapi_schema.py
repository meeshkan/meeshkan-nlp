import os
import json
from meeshkan.nlp.schema_normalizer.schema_paths.parse_openapi_schema import parse_schema


def test_op_parse_schema():
    opbank_filepath = os.path.abspath('../../../../resources/op_spec.json')
    with open(opbank_filepath, encoding='utf8') as f:
        openapi_specs = json.load(f)
    path_tuple = (
        '/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw',
        '/accounts/v3/accounts')
    specs1 = openapi_specs['paths'][path_tuple[0]]['get']['responses']['200']['content']['application/json']['schema']

    parsed_schema_list = [{'$schema': ['_links',
   '_links#self',
   '_links#self#href',
   '_links#transactions',
   '_links#transactions#href',
   'accountId',
   'balance',
   'currency',
   'identifier',
   'identifierScheme',
   'name',
   'nickname',
   'servicerIdentifier',
   'servicerScheme']},
 {'_links@object': ['self', 'self#href', 'transactions', 'transactions#href']},
 {'_links@object#self@object': ['href'],
  '_links@object#transactions@object': ['href']}]


    assert parse_schema(specs1) == parsed_schema_list
