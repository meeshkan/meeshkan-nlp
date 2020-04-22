import math

from meeshkan_nlp.schema_similarity.fields_similarity import FieldsIOUSimilariaty


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


def test_keep_only_alpha(fields_embeddings_similarity):
    # fields_embeddigs_similarity object is instantiated in /tests/conftest.py

    tokens = ["business", "alpha9", "_links"]
    result = ["business", "alpha", "links"]
    assert fields_embeddings_similarity.keep_only_alpha(tokens) == result


def test_find_lema_word(fields_embeddings_similarity):
    assert fields_embeddings_similarity.find_lemma_word("businesses") == "business"
    assert fields_embeddings_similarity.find_lemma_word("accounts") == "account"


def test_convert_lower_word(fields_embeddings_similarity):
    assert fields_embeddings_similarity.convert_lower_word("Meeshkan") == "meeshkan"
    assert fields_embeddings_similarity.convert_lower_word("meeshkan") == "meeshkan"


def test_join_into_sentence(fields_embeddings_similarity):
    assert (
        fields_embeddings_similarity.join_into_sentence(["meeshkan", "rocks", "world"])
        == "meeshkan rocks world"
    )


def test_sentence_vector(fields_embeddings_similarity):
    vector = fields_embeddings_similarity.sentence_vector(
        ["meeshkan", "rocks", "world"]
    )
    assert vector.shape == (300,)


def test_generate_nlp_vector(fields_embeddings_similarity):
    vector = fields_embeddings_similarity.generate_nlp_vector(
        ["meeshkan", "rocks", "the", "world"]
    )
    assert vector.shape == (300,)


def test_embeddings_similarity(fields_embeddings_similarity):
    a = {"accounts", "payments", "links", "balances"}
    b = {"accounts", "payments", "links", "balances", "payer", "receiver"}

    result = fields_embeddings_similarity.similarity(a, b)
    assert result > 0 and result < 1
