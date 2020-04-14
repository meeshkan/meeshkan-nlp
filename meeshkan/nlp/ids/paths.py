"""Code for working with OpenAPI paths, e.g., matching request path to an OpenAPI endpoint with parameter."""
import re
import typing
from typing import Pattern, Tuple

# Pattern to match to in the escaped path string
# Search for occurrences such as "{id}" or "{key-name}"
PATH_PARAMETER_PATTERN = r"""\\{([\w-]+)\\}"""

PATH_PARAMETER_REGEX = r"""([^/#]+)"""


def path_to_regex(path: str) -> Tuple[Pattern[str], Tuple[str]]:
    """Convert an OpenAPI path such as "/pets/{id}" to a regular expression. The returned regular expression
    contains capturing groups for path parameters. Parameter names are returned in the second tuple.

    Arguments:
        path {str} -- [description]

    Returns:
        {} -- Tuple containing (1) pattern for path with parameters replaced by regular expressions, and (2) list of parameters with names.
    """

    # Work on string whose regex characters are escaped ("/"" becomes "//" etc.)
    # This makes it easier to replace matches with regular expressions.
    # For example: /pets/{id} becomes \/pets\/\{id\}
    escaped_path = re.escape(path)

    param_names: typing.List[str] = []  # type

    for match in re.finditer(PATH_PARAMETER_PATTERN, escaped_path):
        full_match = match.group(0)
        param_name = match.group(1)

        param_names.append(param_name)

        escaped_path = escaped_path.replace(full_match, PATH_PARAMETER_REGEX)

    regex_pattern = re.compile(r'^' + escaped_path + r'(?:\?|#|$)')

    return (regex_pattern, tuple(param_names))
