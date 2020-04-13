import typing
from collections import defaultdict
from dataclasses import dataclass

from meeshkan.nlp.schema_normalizer.schema_paths.parse_openapi_schema import (
    parse_schema,
)
from meeshkan.nlp.schema_normalizer.schema_paths.schema_compare import (
    compare_nested_schema,
)
from meeshkan.nlp.schema_normalizer.schema_paths.schema_to_vector import (
    create_object_structure,
    generate_nested_object,
)


def find_best_match(initial_schemas):
    return initial_schemas


def check_and_create_ref(specs, path_tuple, entity_name):
    """Returns the modified open api specs with #ref component for
    similar paths entity.

    Arguments:
        specs {dict} -- Open API specs dict
        path_tuple {tuple} -- similar paths to be analysed
        entity_name {str} -- entity name to be used for #ref component

    Returns:
         Tuple[bool, dict] -- old or modified specs, bool is True if modified
    """
    all_paths_dict = defaultdict(dict)
    nested_paths_dict = all_paths_dict.copy()
    allowed_methods = {"get", "post"}

    initial_schemas = []

    # for path in path_tuple:
    #     for method in specs["paths"][path].keys():
    #         if method in allowed_methods:
    #             initial_schemas.append(SchemaWithLocation(path=path, method=method, code="200", schema_path=(), schema=
    #             specs["paths"][path][method]["responses"]["200"]["content"][
    #                 # TODO need to fix that too
    #                 "application/json"
    #             ]["schema"]))

    all_paths_dict = {key: [] for key in path_tuple}
    nested_paths_dict = all_paths_dict.copy()
    methods = ["get", "post"]

    for path in path_tuple:
        for method in specs["paths"][path].keys():
            if method in methods:
                schema = specs["paths"][path][method]["responses"]["200"]["content"][
                    "application/json"
                ]["schema"]
                all_paths_dict[path].append({method: schema})
                break
                # Now lets us get the nested structure for schema
    for keys, values in all_paths_dict.items():
        for method in values[0].keys():
            nested_paths_dict[keys] = parse_schema(values[0][method])

    # Now we need to compare the two schemas for best refernce
    best_tuple = compare_nested_schema(
        nested_paths_dict[path_tuple[0]], nested_paths_dict[path_tuple[1]]
    )

    if isinstance(best_tuple, list) and len(best_tuple) > 0:
        ref_component = create_ref_path(entity_name)
        ref_component_obj = create_ref_obj(
            all_paths_dict, path_tuple, best_tuple[0], entity_name
        )
        ref_replaced_dict = create_replaced_ref(
            all_paths_dict, path_tuple, best_tuple[0], ref_component
        )
        if len(ref_replaced_dict) != 2:
            return (False, specs)
        # Now update the original specs by replacing the ref components
        for path in path_tuple:
            for method in all_paths_dict[path][0].keys():  # this will run just once
                specs["paths"][path][method]["responses"]["200"]["content"][
                    "application/json"
                ]["schema"] = ref_replaced_dict[path]
        # Now lastly we add the component schema under specs
        specs.update(ref_component_obj)
        return (True, specs)
    else:
        return (False, specs)


def create_replaced_ref(all_paths_dict, path_tuple, tuple1, component_path):
    schemas_list = list()
    for paths in path_tuple:
        for schema in all_paths_dict[paths][0].values():
            schemas_list.append(schema)

    ref_replaced_dict = dict()
    for index, schema in enumerate(schemas_list):
        if tuple1[index] == "$schema":
            ref_replaced_dict[path_tuple[index]] = {"$ref": component_path}
        else:
            schema_copy = schema.copy()
            ref_schema = generate_replaced_ref(
                schema_copy, tuple1[index], component_path
            )
            if ref_schema.get("$schema") is not None:
                del ref_schema["$schema"]
            ref_replaced_dict[path_tuple[index]] = ref_schema
    return ref_replaced_dict


def generate_replaced_ref(schema, parent_name, component_path):
    structure_list = create_object_structure(parent_name)
    len_of_structure = len(structure_list)
    if len_of_structure < 2:
        raise ValueError("The parent property may be not correct")
    schema = check_and_replace(schema, structure_list, component_path)
    return schema


def check_and_replace(top_schema, structure_list, component_path):
    schema = top_schema
    for idx in range(len(structure_list) - 1):
        schema = schema[structure_list[idx]]

    key = structure_list[-1]
    if schema[key]["type"] == "array":
        schema[key]["items"] = {"$ref": component_path}
    else:
        schema[key] = {"$ref": component_path}
    return top_schema


def create_ref_obj(all_paths_dict, path_tuple, tuple1, component_name):
    # Now we are going to make reference to the same matched nested structure so
    # for convenience let us just refer to the first element of the path tuple

    ref_index = 1
    # Te beow loop will run only once.
    for method, schema in all_paths_dict[path_tuple[ref_index]][0].items():
        root_property = tuple1[ref_index]
        if root_property == "$schema":
            return generate_component_dict(schema, component_name)
        else:
            nested_schema = generate_nested_object(schema, root_property)
            return generate_component_dict(nested_schema, component_name)


def generate_component_dict(schema, component_name):
    obj_list = [component_name, "schemas", "components"]
    obj_dict = schema
    for item in obj_list:
        obj_dict = {item: obj_dict}
    return obj_dict


def create_ref_path(entity_name):
    return f"#/components/schemas/{entity_name}"
