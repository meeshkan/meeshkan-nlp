import os
import json
from meeshkan.nlp.schema_normalizer.schema_paths.schema_to_vector import create_object_structure, \
    generate_child_vectors, generate_schema_vectors


def test_create_object_structure():
    obj = 'users@array#name@object#first@string'
    assert create_object_structure(obj) == ['properties', 'users', 'items', 'properties', 'name']

    obj = 'users@object#courses@array#name@string'
    assert create_object_structure(obj) == ['properties', 'users', 'properties', 'courses', 'items']

    obj = 'users@array'
    assert create_object_structure(obj) == ['properties', 'users']

    obj = 'users@object'
    assert create_object_structure(obj) == ['properties', 'users']



# Let us fetch some data from openapi specs for opbank
opbank_filepath = os.path.abspath('../../../../resources/op_spec.json')
with open(opbank_filepath, encoding='utf8') as f:
    openapi_specs = json.load(f)
path_tuple = (
        '/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw',
        '/accounts/v3/accounts')
specs1 = openapi_specs['paths'][path_tuple[0]]['get']['responses']['200']['content']['application/json']['schema']

# we need to have a key '$schema' with any value in the root for functions to work
specs1['$schema'] = 'root'

def test_generate_child_vectors():
    result = ['accountId@string',
 'identifier@string',
 'identifierScheme@string',
 'nickname@string',
 'name@string',
 'balance@integer',
 'currency@string',
 'servicerScheme@string',
 'servicerIdentifier@string',
 '_links@object']

    assert generate_child_vectors(specs1) == result

def test_generate_schema_vectors():
    result = ['accountId@string',
 'identifier@string',
 'identifierScheme@string',
 'nickname@string',
 'name@string',
 'balance@integer',
 'currency@string',
 'servicerScheme@string',
 'servicerIdentifier@string',
 '_links@object',
 '_links@object#self@object',
 '_links@object#transactions@object',
 '_links@object#self@object#href@string',
 '_links@object#transactions@object#href@string']

    assert generate_schema_vectors(specs1) == result
