import itertools
import typing
from abc import ABC, abstractmethod
from spacy.language import Language
import typing
import re
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances


class FieldsSimilarityBase(ABC):
    group_threshold = 0.6

    @abstractmethod
    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        pass

    def group_similarity(self, group: typing.Iterable[typing.Set[str]]) -> float:
        total_score = 0.0
        total_count = 0
        for a, b in itertools.combinations(group, r=2):
            total_score += self.similarity(a, b)
            total_count += 1
        avg = total_score / total_count

        return 0 if avg < self.group_threshold else avg


class FieldsIOUSimilariaty(FieldsSimilarityBase):
    score_threshold = 0.6

    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        intersection = len(a.intersection(b))
        if intersection == 0:
            return 0

        union = len(a.union(b))

        score = intersection / union

        return 0 if score < self.score_threshold else score


class FieldsEmbeddingsSimilariaty(FieldsSimilarityBase):  # TODO  Nakul implement it
    def __init__(self, nlp: Language):
        self._nlp = nlp

    def keep_only_alpha(self, tokens_list: typing.List) -> typing.List[str]:
        list_of_words = list()
        for word in tokens_list:
            word = re.sub(r"[^a-zA-Z]", " ", word)
            word = word.split()
            list_of_words += word

        return list_of_words

    def find_lemma_word(self, word: str) -> str:
        return self._nlp(word)[0].lemma_

    def find_lemma_list(self, tokens_list: typing.List[str]) -> typing.List[str]:
        return [self.find_lemma_word(word) for word in tokens_list]

    def remove_duplicate_and_sort(self, tokens_list: typing.List) -> typing.List[str]:
        return sorted(list(set(tokens_list)))

    def convert_lower_word(self, word: str) -> str:
        return word.lower()

    def convert_lower_list(self, tokens_list: typing.List[str]) -> typing.List[str]:
        return [self.convert_lower_word(word) for word in tokens_list]

    def join_into_sentence(self, tokens_list: typing.List, separator=" ") -> str:
        return separator.join(tokens_list)

    def sentence_vector(self, tokens_list: typing.List):
        sentence = self.join_into_sentence(tokens_list)
        return self._nlp(sentence).vector

    def generate_nlp_vector(self, tokens_list: typing.List):
        tokens_list = self.keep_only_alpha(tokens_list)
        #tokens_list = self.camel_case_split_list(tokens_list)
        tokens_list = self.convert_lower_list(tokens_list)
        tokens_list = self.find_lemma_list(tokens_list)
        tokens_list = self.remove_duplicate_and_sort(tokens_list)

        return self.sentence_vector(tokens_list)


    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        # raise NotImplementedError()

        if len(a) == 0:
            raise ValueError("Input set of fields 'a' is empty")
        if len(b) == 0:
            raise ValueError("Input set of fields 'b' is empty")

        vec_a = self.generate_nlp_vector(list(a))
        vec_b = self.generate_nlp_vector(list(b))

        a_rows = vec_a.shape[0]
        b_rows = vec_b.shape[0]

        vec_a = vec_a.reshape(1, a_rows)
        vec_b = vec_b.reshape(1, b_rows)

        distance = pairwise_distances(X=vec_a, Y=vec_b, metric='cosine')
        f_distance = float(distance[0][0])
        return f_distance