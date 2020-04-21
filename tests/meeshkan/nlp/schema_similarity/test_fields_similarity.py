import math

from meeshkan.nlp.schema_similarity.fields_similarity import FieldsIOUSimilariaty


def test_iou_similarity_pair():
    similarity = FieldsIOUSimilariaty()
    assert similarity.similarity({"a", "b", "c"}, {"a", "b", "c"}) == 1
    assert similarity.similarity({"a", "b", "c", "d"}, {"a", "b", "c", "f"}) == 0.6
    assert similarity.similarity({"a", "b", "c", "d"}, {"a", "b", "c", "f", "g"}) == 0


def test_iou_similarity_group():
    similarity = FieldsIOUSimilariaty()
    assert (
        similarity.group_similarity(({"a", "b", "c"}, {"a", "b", "c"}, {"a", "b", "c"}))
        == 1
    )
    assert (
        similarity.group_similarity(
            ({"a", "b", "c", "d"}, {"a", "b", "c", "f"}, {"a", "b", "c", "g"})
        )
        == 0.6
    )
    assert math.isclose(
        similarity.group_similarity(
            ({"a", "b", "c", "d"}, {"a", "b", "c", "f"}, {"a", "b", "c", "f"})
        ),
        0.733,
        rel_tol=1e-3,
    )
    assert (
        similarity.group_similarity(
            ({"a", "b", "c", "d"}, {"a", "b", "c", "f", "g"}, {"a", "b", "c", "d"})
        )
        == 0
    )
