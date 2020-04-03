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



def test_generate_child_vectors(accounts_schema):
    result = ['accountId@string',
 'identifier@string',
 'identifierScheme@string',
 'nickname@string',
 'name@string',
  'currency@string',
  'servicerScheme@string',
  'servicerIdentifier@string',
  'balance@integer',
 '_links@object']

    assert set(generate_child_vectors(accounts_schema)) == set(result)  # check equality without specific order

def test_generate_schema_vectors(accounts_schema):
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

    assert generate_schema_vectors(accounts_schema) == result
