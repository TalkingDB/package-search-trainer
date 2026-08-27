from unittest.mock import MagicMock, patch

from talkingdb_st.services.crawl.fetcher import FetchError
from talkingdb_st.services.train.orchestrator import crawl_and_index

PAGE_HTML = "<html><body><h1 class='title'>Hello World</h1></body></html>"


def test_crawl_and_index_happy_path():
    ds_client = MagicMock()

    with patch(
        "talkingdb_st.services.train.orchestrator.fetch_page",
        return_value=PAGE_HTML,
    ):
        result = crawl_and_index(
            ds_client,
            "acme",
            ["https://example.com/a"],
            {"title": "h1.title"},
            content_field="title",
            chunk_size=5,
            overlap=0,
        )

    assert result == {
        "pages_crawled": 1,
        "chunks_indexed": 1,
        "failures": [],
    }

    ds_client.train_vectors.assert_called_once_with(
        "acme",
        [["https://example.com/a#chunk0"], ["Hello World"]],
        vector_index=1,
        partition=None,
    )
    ds_client.train_keywords.assert_called_once_with(
        "acme",
        [{"title": "Hello World", "id": "https://example.com/a#chunk0"}],
        id_field="id",
        partition=None,
    )


def test_crawl_and_index_records_fetch_failures_and_continues():
    ds_client = MagicMock()

    def fake_fetch(url, *args, **kwargs):
        if url == "https://example.com/bad":
            raise FetchError("boom")
        return PAGE_HTML

    with patch(
        "talkingdb_st.services.train.orchestrator.fetch_page", side_effect=fake_fetch
    ):
        result = crawl_and_index(
            ds_client,
            "acme",
            ["https://example.com/bad", "https://example.com/good"],
            {"title": "h1.title"},
            content_field="title",
        )

    assert result["pages_crawled"] == 1
    assert result["chunks_indexed"] == 1
    assert result["failures"] == [{"url": "https://example.com/bad", "error": "boom"}]


def test_crawl_and_index_skips_training_when_nothing_indexed():
    ds_client = MagicMock()

    with patch(
        "talkingdb_st.services.train.orchestrator.fetch_page",
        side_effect=FetchError("boom"),
    ):
        result = crawl_and_index(
            ds_client,
            "acme",
            ["https://example.com/a"],
            {"title": "h1.title"},
            content_field="title",
        )

    assert result == {
        "pages_crawled": 0,
        "chunks_indexed": 0,
        "failures": [{"url": "https://example.com/a", "error": "boom"}],
    }
    ds_client.train_vectors.assert_not_called()
    ds_client.train_keywords.assert_not_called()


def test_crawl_and_index_uses_custom_id_field_and_partition():
    ds_client = MagicMock()

    with patch(
        "talkingdb_st.services.train.orchestrator.fetch_page",
        return_value=PAGE_HTML,
    ):
        crawl_and_index(
            ds_client,
            "acme",
            ["https://example.com/a"],
            {"title": "h1.title"},
            content_field="title",
            id_field="doc_id",
            partition="tenant-1",
            chunk_size=5,
            overlap=0,
        )

    _, kwargs = ds_client.train_keywords.call_args
    assert kwargs["id_field"] == "doc_id"
    assert kwargs["partition"] == "tenant-1"
    assert ds_client.train_keywords.call_args[0][1][0]["doc_id"] == (
        "https://example.com/a#chunk0"
    )
