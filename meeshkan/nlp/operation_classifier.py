import typing


class OperationClassifier:
    def fill_operations(self, spec: typing.Any) -> typing.Any:
        for pathname, path_item in spec["paths"].items():
            for method_name, operation in path_item.items():
                if method_name == "get":
                    operation["x-meeshkan-operation"] = "read"
                elif method_name == "delete":
                    operation["x-meeshkan-operation"] = "delete"
                elif method_name == "post" or method_name == "put":
                    request_body = (
                        operation.get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema")
                    )
                    if request_body is not None:
                        operation["x-meeshkan-operation"] = "upsert"

        return spec
