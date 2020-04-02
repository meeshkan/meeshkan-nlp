import copy

from openapi_typed_2 import OpenAPIObject, convert_from_openapi, convert_to_openapi


class SpecOptimizer:
    def __init__(self):
        pass

    def optimize_spec(self, spec: OpenAPIObject) -> OpenAPIObject:
        spec_dict = copy.deepcopy(convert_from_openapi(spec))
        return convert_to_openapi(spec_dict)
