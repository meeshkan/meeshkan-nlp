from meeshkan.nlp.schema_normalizer.schema_relations.feature_extraction import (
    FeatureExtraction,
)

fe = FeatureExtraction()


def test_keep_only_alpha():
    tokens = ["business", "alpha9", "_links"]
    result = ["business", "alpha", "links"]
    assert fe.keep_only_alpha(tokens) == result


def test_is_camel_case():
    assert fe.is_camel_case("meeshkanRocks") == True
    assert fe.is_camel_case("MeeshkanRocks") == True
    assert fe.is_camel_case("Meeshkanrocks") == False
    assert fe.is_camel_case("meeshkanrocks") == False


def test_camel_case_split_word():
    assert fe.camel_case_split_word("meeshkanRocks") == ["meeshkan", "Rocks"]
    assert fe.camel_case_split_word("meeshkan") == ["meeshkan"]
    assert fe.camel_case_split_word("MeeshkanRocks") == ["Meeshkan", "Rocks"]


def test_find_lema_word():
    assert fe.find_lemma_word("businesses") == "business"
    assert fe.find_lemma_word("accounts") == "account"


def test_convert_lower_word():
    assert fe.convert_lower_word("Meeshkan") == "meeshkan"
    assert fe.convert_lower_word("meeshkan") == "meeshkan"


def test_join_into_sentence():
    assert (
        fe.join_into_sentence(["meeshkan", "rocks", "world"]) == "meeshkan rocks world"
    )


def test_sentence_vector():
    vector = fe.sentence_vector(["meeshkan", "rocks", "world"])
    assert vector.shape == (300,)


def test_generate_nlp_vector():
    vector = fe.generate_nlp_vector(["meeshkan", "rocks", "the", "world"])
    assert vector.shape == (300,)
