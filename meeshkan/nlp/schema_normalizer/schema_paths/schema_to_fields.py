'''
    This module is to parse the schema features and return the list of schema fields
'''
import re
from meeshkan.nlp.schema_normalizer.schema_paths.schema_to_vector import split_type, split_level
from meeshkan.nlp.schema_normalizer.schema_paths.schema_to_vector import _object, _array, _string, _integer, _number, _boolean, _unknown

def split_by_type(obj):
    return obj.split(split_type)

def split_by_level(obj):
    return obj.split(split_level)


def split_by_all(obj):
    list1 = split_by_level(obj)
    list2 = []
    for item in list1:
        list2.append(split_by_type(item))
    return list2

def create_split_level(obj, order=None, only=False):
    if order is None or order == 0:
        fields = split_by_all(obj)
        return [field[0] for field in fields]
    else:
        if not only:
            fields = split_by_all(obj)
            return [field[0] for field in fields[:order]]
        else:
            fields = split_by_all(obj)
            if len(fields) > order:
                return [fields[order - 1][0]]
            else:
                return [fields[-1][0]]


def parse_schema_features(obj, order=None, only=False):
    """Removes the structure type '@type' out of property

    Arguments:
        obj {list} -- list of property@type features

    Returns:
        list -- list of properties parsed
    """
    if not isinstance(obj, list):
        raise TypeError('The schema features in input argument is not a list')
    if order is not None:
        if not isinstance(order, int):
            raise TypeError('The order argument can be None or integer')
    if not isinstance(only, bool):
        raise TypeError("The argument 'only' can be only boolean")
    
    if len(obj) == 0:
        return []
    fields_list = []
    for schema_string in obj:
        fields_list += create_split_level(schema_string, order=order, only=only)
    return fields_list
    

def schema_remove_types(obj):
    """Removes the type our of schema properties

    Arguments:
        obj {list} -- list of schema properties

    Returns:
        list -- list of parsed schema properties
    """
    if not isinstance(obj, str):
        raise TypeError('The object must be a type str')
    sub_expression = split_type + _object + '|' + \
                    split_type + _array + '|' + \
                    split_type + _string + '|' + \
                    split_type + _number + '|' + \
                    split_type + _integer + '|' + \
                    split_type + _boolean + '|' + \
                    split_type + _unknown

    return re.sub(sub_expression, '', obj)