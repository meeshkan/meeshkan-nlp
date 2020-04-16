import itertools
import typing
from abc import ABC, abstractmethod


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
    def similarity(self, a: typing.Set[str], b: typing.Set[str]) -> float:
        raise NotImplementedError()
