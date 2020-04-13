import itertools
from abc import ABC, abstractmethod

import typing


class FieldsSimilarityBase(ABC):
    score_threshold = 0.7

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
        if avg < self.score_threshold:
            return 0
        return avg


class FieldsIOUSimilariaty(FieldsSimilarityBase):
    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        intersection = len(a.intersection(b))
        if intersection == 0:
            return 0

        union = len(a.union(b))

        return intersection/union


class FieldsEmbeddingsSimilariaty(FieldsSimilarityBase): #TODO  Nakul implement it
    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        raise NotImplementedError()
