import re
import string
import typing
from typing import Sequence

import spacy
from spacy.language import Language

from meeshkan.nlp.ids.gib_detect import GibberishDetector
from meeshkan.nlp.ids.id_classifier import IdClassifier, IdType
from openapi_typed_2 import OpenAPIObject


def _make_dict_from_2_lists(list1, list2):  # TODO Maria Use dict(zip) instead of it
    """Make a dictionary from two lists

    Example:
    >>>list1=['a','b','c']
    >>>list2=[1,2,3]
    >>> _make_dict_from_2_lists(list1, list2)
    {'a':1,'b':2,'c':3}

    Arguments:
        two lists
    Returns:
        Dist[str/int]
    """
    dict_1 = {}
    for key, value in zip(list1, list2):
        if key not in dict_1:
            dict_1[key] = [value]
        else:
            dict_1[key].append(value)
    return dict_1


def _camel_case(example: str) -> bool: #TODO Maria move it into utils/global tokenize
    """This fubction recognize camel case.

    Example:

    >>> _camel_case('BodyAsJson')
    True

    Return:
        True or False
    """
    # for i in string.punctuation:
    if any(x in example for x in string.punctuation) == True:
        return False
    else:
        if any(list(map(str.isupper, example[1:-1]))) == True:
            return True
        else:
            return False


def _camel_case_split(s: str) -> Sequence[str]:
    """This function split camel case words into pieces.

        Example:

        >>> _camel_case_split('BodyAsJson')
        ['Body', 'As', 'Json']

        Return:
            List
        """
    idx = list(map(str.isupper, s))
    # mark change of case
    l = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:  # "Ul"
            l.append(i)
        elif not x and y:  # "lU"
            l.append(i + 1)
    l.append(len(s))
    # for "lUl", index of "U" will pop twice, have to filer it
    return [s[x:y] for x, y in zip(l, l[1:]) if x < y]


class EntityExtractorNLP:
    STOP_WORDS = [r"api.*", "json", "yaml", "html", "config"]
    STOP_TAGS = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}

    def __init__(self, nlp: Language):
        self.nlp = nlp #TODO Maria all private fields should start with _
        self.gib_detector = GibberishDetector()
        self._id_detector = IdClassifier()

    def tokenize2(
        self, path_list: list
    ) -> Sequence[str]:  # TODO Maria Why is it tokenize<<2>>?
        """This function tokenize list of words and remove potential ids .

            Example:

            >>> tokenize2(['libs', 'granite', 'core', 'content', 'login', '123ad8797'])
            ['libs', 'granite', 'core', 'content', 'login']

            Return:
                List
            """
        res = list()
        for item in path_list:
            if self._id_detector.by_value(item) != IdType.UNKNOWN:
                if len(item) > 3:
                    pass
            else:
                item = re.sub("[^0-9a-z-A-Z]+", " ", item)
                item = re.sub("[0-9]+", "", item)
                item = re.sub("-", " ", item)
                for word in item.split(" "):
                    if _camel_case(word):
                        camel_list = _camel_case_split(word)
                        for cam in camel_list:
                            res.append(cam.lower())
                    else:
                        if len(word) > 3:
                            if word in self.nlp.vocab:
                                res.append(word)
                            else:
                                try:
                                    word_list = self.split_to_words(word)
                                    for w in word_list:
                                        res.append(w)
                                except IndexError:
                                    pass
                        if len(word) == 3:
                            if not self.gib_detector.is_gibberish(word):
                                res.append(word)
        return res

    def _split_pathes(self, p_list: list) -> Sequence[str]:
        """This function removes stop words and verbs from the list and tokenizes it.

        Example:

        >>> _split_pathes(['libs', 'push', 'v1', 'content', 'login', '123ad8797'])
        ['libs', 'content', 'login']

        Return:
            List
        """
        path_lists = []
        # print(self.tokenize2(p_list))
        path_list = [
            item for item in self.tokenize2(p_list) if not self._is_stop_word(item)
        ]
        # print(path_list)
        path_list = [
            word for word in path_list if self.nlp(word)[0].tag_ not in self.STOP_TAGS
        ]
        path_lists.append(path_list)
        return path_list

    def get_entity_from_url(
        self, p_list: list
    ) -> str:  # TODO Maria. It's not an url. URL is http://google.com/something. It's a path.
        """This function return lemmatized entity from the path.

        Example:

        >>> get_entity_from_url('/analyzer/12abd345/archive-rule/12abd345')
        'rule'

        Return:
            string or None
        """
        if len(self._split_pathes(p_list)) >= 1:
            return self.nlp(self._split_pathes(p_list)[-1])[0].lemma_
        else:
            return "None"
        # return self._mapping.get(path)

    def _is_stop_word(self, path_item: str) -> bool:
        """This function recognizes stop words in the list.

        Example:

        >>> _is_stop_word('api')
        'True'

        Return:
            True if it is stop word
             or False if not
        """
        for stop_word in self.STOP_WORDS:
            if re.match(stop_word, path_item):
                return True
        return False

    def get_positions(self, long_string: str) -> typing.Iterable[int]:
        """This function return position of the new word in the long string without space

        Example:

        >>> get_positions('truststorepush')
        [5, 10]

        Return:
            list
        """
        kl: typing.List[int] = []
        for i in range(2, len(long_string) - 2):
            if long_string[i:] in self.nlp.vocab:
                kl.append(i)
        if long_string[0 : kl[0]] in self.nlp.vocab:
            yield (kl[0])
        else:
            yield (kl[0])
            yield from self.get_positions(long_string[0 : kl[0]])

    # This function split long string to parts
    def split_to_words_gen(self, long_string: str):
        """Split long string into words.

        Arguments:
            long_string {str} -- Long string of words

        Yields:
            [str] -- Word
        """
        final_res = [i for i in self.get_positions(long_string)]
        final_res.append(0)
        final_res.append(len(long_string))
        f_res = sorted(final_res)
        for i in range(len(f_res) - 1):
            yield (long_string[f_res[i] : f_res[i + 1]])

    def split_to_words(self, long_string: str) -> Sequence[str]:
        """Split long string into words.

        Example:

        >>> split_to_words(truststore)
        ["trust", "store"]

        Arguments:
            long_string {[type]} -- Long string of words

        Returns:
            List[str] -- Splitted words.
        """
        return list(self.split_to_words_gen(long_string))

    def get_path_entity(self, path):
        """Split long string into words.

        Example:

        >>> get_path_entity('truststore/users')
        ('truststore/users', 'user')

        Arguments:
            String

        Returns:
            tuple
        """
        return (path, self.get_entity_from_url(path.split("/")[1:]))

    def get_entity_from_spec(self, spec: OpenAPIObject):
        """Extract pathes from the yaml file and make dictionary with entity and corresponding pathes

        Example:

        >>> get_entity_from_spec('openapi.yaml')
        {'transfer': ['/api/rest/v1/account/transfer'], 'user': ['/api/rest/v1/account/user', '/api/rest/v1/account/user/id']}

        Arguments:
            name of the file ->> String
        Returns:
            Dictionary[str]---key is an entity and value is a list of pathes corresponding to this entity

        """
        ent = []
        pathes1 = []
        for path in spec.paths.keys():
            item = path.split("/")[1:]
            count = 0
            for i in item:
                if i is not "":
                    count += 1
            if count > 1:
                check_path = re.sub(r"\{.*?\}", "id", path)
                ent.append(self.get_entity_from_url(check_path.split("/")[1:]))
                pathes1.append(path)
        return _make_dict_from_2_lists(ent, pathes1)


EntityExtractor = EntityExtractorNLP
