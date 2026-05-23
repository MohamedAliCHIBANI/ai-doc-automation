import pytest
from app.services.file_loader import load_file


def test_txt_returns_decoded_text():
    assert load_file("note.txt", b"Hello world") == "Hello world"


def test_csv_returns_tabular_text():
    csv = b"name,age\nAlice,30\nBob,25"
    result = load_file("data.csv", csv)
    assert "Alice" in result
    assert "Bob" in result


def test_unsupported_extension_raises():
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_file("doc.docx", b"data")


def test_extension_check_is_case_insensitive():
    # .TXT should work the same as .txt
    result = load_file("NOTE.TXT", b"hello")
    assert result == "hello"
