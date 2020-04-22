from meeshkan_nlp.ids.gib_detect import GibberishDetector


def test_gib_detector():
    detector = GibberishDetector()

    assert not detector.is_gibberish("gibberish")
    assert not detector.is_gibberish("gibberish text")
    assert not detector.is_gibberish("gibberish_text_with_underscores")
    assert not detector.is_gibberish("gibberish.text.with.dots")
    assert not detector.is_gibberish("gibberish-text-with-minus")

    assert detector.is_gibberish("WhYHJKb")
    assert detector.is_gibberish("cdkf=9m0fm3")
    assert not detector.is_gibberish("g5ibdf35ber6ish")
