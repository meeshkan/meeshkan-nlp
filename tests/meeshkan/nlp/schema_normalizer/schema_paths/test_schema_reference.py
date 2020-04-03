import os
import json
from meeshkan.nlp.schema_normalizer.schema_paths.schema_reference import create_ref_path, \
generate_component_dict, create_ref_obj, generate_replaced_ref, \
    create_replaced_ref

opbank_original_filepath = os.path.abspath('tests/resources/op_spec.json')
with open(opbank_original_filepath, encoding='utf8') as f:
    specs = json.load(f)

path_tuple = (
        '/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw',
        '/accounts/v3/accounts')

entity_name = 'account'
best_tuple = ('$schema', 'accounts@array')
all_paths_dict = {key : [] for key in path_tuple}
methods = ['get', 'post']
for path in path_tuple:
    for method in specs['paths'][path].keys():
        if method in methods:
            schema = specs['paths'][path][method]['responses']['200']['content']['application/json']['schema']
            all_paths_dict[path].append({method: schema})
            break  # To ensure that only single method is picked for any endpoint



def test_create_ref_path():
    assert create_ref_path('account') == '#/components/schemas/account'


def test_generate_component_dict():
    component_name = 'account'
    init_obj = {
        'name' : 'nakul',
    }
    transformed_obj = {
        'components' : {
            'schemas' : {
                component_name : init_obj
            }
        }
    }

    assert generate_component_dict(init_obj, component_name) == transformed_obj

def test_create_ref_obj():
    result = {'components': {'schemas': {'account': {'required': ['_links',
     'accountId',
     'balance',
     'currency',
     'identifier',
     'identifierScheme',
     'name',
     'nickname',
     'servicerIdentifier',
     'servicerScheme'],
    'properties': {'accountId': {'type': 'string'},
     'identifier': {'type': 'string'},
     'identifierScheme': {'type': 'string'},
     'nickname': {'type': 'string'},
     'name': {'type': 'string'},
     'balance': {'type': 'number'},
     'currency': {'type': 'string'},
     'servicerScheme': {'type': 'string'},
     'servicerIdentifier': {'type': 'string'},
     '_links': {'required': ['self', 'transactions'],
      'properties': {'self': {'required': ['href'],
        'properties': {'href': {'type': 'string'}},
        'type': 'object'},
       'transactions': {'required': ['href'],
        'properties': {'href': {'type': 'string'}},
        'type': 'object'}},
      'type': 'object'}},
    'type': 'object'}}}}


    assert create_ref_obj(all_paths_dict, path_tuple, best_tuple, entity_name) == result


def test_generate_replaced_ref():
    result = {'required': ['_links', 'accounts'],
 'properties': {'accounts': {'$ref': '#/components/schemas/account'},
  '_links': {'required': ['self'],
   'properties': {'self': {'required': ['href'],
     'properties': {'href': {'type': 'string'}},
     'type': 'object'}},
   'type': 'object'}},
 'type': 'object',
 '$schema': 'root'}

    specs = all_paths_dict[path_tuple[1]][0]['get']
    specs_copy = specs.copy()
    specs_copy['$schema'] = 'root'
    assert generate_replaced_ref(specs_copy,
                                 'accounts@array',
                                 '#/components/schemas/account') == result
def test_create_replaced_ref():
    result = {'/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw': {'$ref': '#/components/schemas/account'},
 '/accounts/v3/accounts': {'required': ['_links', 'accounts'],
  'properties': {'accounts': {'$ref': '#/components/schemas/account'},
   '_links': {'required': ['self'],
    'properties': {'self': {'required': ['href'],
      'properties': {'href': {'type': 'string'}},
      'type': 'object'}},
    'type': 'object'}},
  'type': 'object'}}

    assert create_replaced_ref(all_paths_dict,
                               path_tuple,
                               best_tuple, ''
                                           '#/components/schemas/account') == result

