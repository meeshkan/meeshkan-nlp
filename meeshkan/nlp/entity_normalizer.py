from typing import Tuple

from meeshkan.nlp.schema_normalizer.schema_paths.schema_reference import (
    check_and_create_ref,
)
from meeshkan.nlp.schema_normalizer.schema_relations.schema_distance import (
    calc_distance,
)
from openapi_typed_2 import OpenAPIObject, convert_from_openapi, convert_to_openapi


class EntityNormalizer:
    def __init__(self,):
        self.entity_name = "account"
        self.path_tuple = (
            "/accounts/v3/accounts/eg9Mno2tvmeEE039chWrHw7sk1155oy5Mha8kQp0mYs.sxajtselenSScKPZrBMYjg.SoFWGrHocw1YoNb3zw-vfw",
            "/accounts/v3/accounts",
        )

    def nearest_path(self, specs: OpenAPIObject):
        """Using NLP word embeddings the function will check the responses of different
        paths and returns the list of pair of paths tuple which are having the
        cosine distance less than a pre-defined threshold = 0.1

        Arguments:
            specs {OpenAPIObject} -- OpenAPI specification
        Returns:
                List -- List of tuple pairs which are having responses very near to each other
        """
        specs_dict = convert_from_openapi(specs)
        paths_tuple_list = calc_distance(specs_dict)
        return paths_tuple_list

    def normalize(
        self, specs: OpenAPIObject, path_tuple: Tuple, entity_name: str
    ) -> OpenAPIObject:
        """Builds the #ref components in an OpenAPI object by understanding similar nested
        sructures for a set of paths.

        Arguments:
            specs {OpenAPIObject} -- The open API specification object
            path_tuple {tuple} -- two different paths which have similar entity
            entity_name {str} -- an derived entity name for the similar paths


        Returns:
            OpenAPIObject -- Old or updated schema if #ref is created
        """
        specs_dict = convert_from_openapi(specs)
        is_updated, updated_specs = check_and_create_ref(
            specs_dict, path_tuple, entity_name
        )

        if is_updated:
            return convert_to_openapi(updated_specs)
        else:
            return specs
