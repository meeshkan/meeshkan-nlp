from meeshkan.nlp.schema_normalizer.schema_paths.schema_compare import exact_match, compare_nested_schema



def test_exact_match():
    list1 = ['business', 'accounts', 'payments']
    list2 = ['business', 'accounts', 'payments']
    assert exact_match(list1, list2) == True

    list1 = ['business', 'accounts', 'payments']
    list2 = ['business', 'accounts', 'payment']
    assert exact_match(list1, list2) == False

    list1 = ['business', 'accounts', 'payments']
    list2 = ['business', 'accounts']
    assert exact_match(list1, list2) == False



def test_compare_nested_schema():
    list1 = [{'$schema': ['_links',
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


    list2 = [{'$schema': ['_links',
   '_links#self',
   '_links#self#href',
   'accounts',
   'accounts#_links',
   'accounts#_links#self',
   'accounts#_links#self#href',
   'accounts#_links#transactions',
   'accounts#_links#transactions#href',
   'accounts#accountId',
   'accounts#balance',
   'accounts#currency',
   'accounts#identifier',
   'accounts#identifierScheme',
   'accounts#name',
   'accounts#nickname',
   'accounts#servicerIdentifier',
   'accounts#servicerScheme']},
 {'accounts@array': ['_links',
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
   'servicerScheme'],
  '_links@object': ['self', 'self#href']},
 {'accounts@array#_links@object': ['self',
   'self#href',
   'transactions',
   'transactions#href'],
  '_links@object#self@object': ['href']},
 {'accounts@array#_links@object#self@object': ['href'],
  'accounts@array#_links@object#transactions@object': ['href']}]



    assert compare_nested_schema(list1, list2) == [('$schema', 'accounts@array')]
    assert compare_nested_schema(list2, list1) == [('accounts@array', '$schema')]