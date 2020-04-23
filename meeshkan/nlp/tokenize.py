import string
from typing import Sequence


def camel_case(example: str) -> bool:
    """This fubction recognize camel case.

    Example:

    >>> _camel_case('BodyAsJson')
    True

    Return:
        True or False
    """
    if any(x in example for x in string.punctuation):
        return False
    else:
        if any(list(map(str.isupper, example[1:-1]))):
            return True
        else:
            return False


def camel_case_split(s: str) -> Sequence[str]:
    """This function split camel case words into pieces.

        Example:

        >>> _camel_case_split('BodyAsJson')
        ['Body', 'As', 'Json']

        Return:
            List
        """
    idx = list(map(str.isupper, s))
    # mark change of case
    change_of_case = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            change_of_case.append(i)
        elif not x and y:  # "lU"
            change_of_case.append(i + 1)
    change_of_case.append(len(s))
    # for "lUl", index of "U" will pop twice, have to filer it
    return [s[x:y] for x, y in zip(change_of_case, change_of_case[1:]) if x < y]