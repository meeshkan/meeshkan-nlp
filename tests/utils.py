from openapi_typed_2 import convert_to_OpenAPIObject


def spec_dict(
    path="/", method="get", response_schema={}, request_schema=None, components=None
):
    spec = {
        "openapi": "3.0",
        "info": {"title": "Title", "version": "1.1.1"},
        "paths": {
            path: {
                method: {
                    "responses": {
                        "200": {
                            "description": "some",
                            "content": {
                                "application/json": {"schema": response_schema}
                            },
                        }
                    }
                }
            }
        },
    }
    if components is not None:
        spec["components"] = components

    if request_schema is not None:
        spec["paths"][path][method]["requestBody"] = {
            "content": {"application/json": {"schema": request_schema}}
        }
    return spec


def spec(
    path="/", method="get", response_schema={}, request_schema=None, components=None
):
    return convert_to_OpenAPIObject(
        spec_dict(path, method, response_schema, request_schema, components)
    )


def add_item(
    spec,
    path="/",
    method="get",
    response_schema={},
    request_schema=None,
    components=None,
):
    if path not in spec["paths"]:
        spec["paths"][path] = {}

    spec["paths"][path][method] = {
        "responses": {
            "200": {
                "description": "some",
                "content": {"application/json": {"schema": response_schema}},
            }
        }
    }
    if components is not None:
        spec["components"] = components

    if request_schema is not None:
        spec["paths"][path][method]["requestBody"] = {
            "content": {"application/json": {"schema": request_schema}}
        }

    return spec
