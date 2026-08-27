import pytest

from talkingdb_st.services.crawl.chunker import chunk_text


def test_chunk_text_returns_empty_list_for_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_returns_single_chunk_when_text_fits():
    text = " ".join(f"w{i}" for i in range(50))

    chunks = chunk_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_splits_with_overlap():
    words = [f"w{i}" for i in range(10)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=5, overlap=2)

    assert chunks == [
        "w0 w1 w2 w3 w4",
        "w3 w4 w5 w6 w7",
        "w6 w7 w8 w9",
    ]


def test_chunk_text_no_overlap():
    words = [f"w{i}" for i in range(6)]
    text = " ".join(words)

    chunks = chunk_text(text, chunk_size=3, overlap=0)

    assert chunks == ["w0 w1 w2", "w3 w4 w5"]


@pytest.mark.parametrize(
    "chunk_size,overlap",
    [
        (0, 0),
        (-1, 0),
        (5, -1),
        (5, 5),
        (5, 6),
    ],
)
def test_chunk_text_rejects_invalid_size_and_overlap(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text here", chunk_size=chunk_size, overlap=overlap)
