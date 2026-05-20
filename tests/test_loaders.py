from app.rag.loaders import _normalize_extracted_text


def test_normalize_single_char_lines():
    broken = "a\nb\nc\nd\n"
    assert _normalize_extracted_text(broken) == "a b c d"


def test_normalize_collapses_repeated_words():
    text = "hello hello world world world"
    assert _normalize_extracted_text(text) == "hello world"


def test_normalize_preserves_normal_paragraph():
    text = "This is a normal sentence about mindfulness."
    assert _normalize_extracted_text(text) == text
