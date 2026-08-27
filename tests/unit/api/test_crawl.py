from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from talkingdb_st.main import app

client = TestClient(app)


def test_crawl_and_train_invokes_orchestrator_with_a_fresh_ds_client():
    fake_ds_client = MagicMock()

    with (
        patch("talkingdb_st.api.crawl.DSClient", return_value=fake_ds_client) as ds_cls,
        patch(
            "talkingdb_st.api.crawl.crawl_and_index",
            return_value={"pages_crawled": 1, "chunks_indexed": 2, "failures": []},
        ) as crawl_and_index,
    ):
        response = client.post(
            "/api/namespaces/acme/crawl",
            json={
                "urls": ["https://example.com/a"],
                "selectors": {"title": "h1.title"},
                "content_field": "title",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"pages_crawled": 1, "chunks_indexed": 2, "failures": []}
    ds_cls.assert_called_once_with()
    crawl_and_index.assert_called_once_with(
        fake_ds_client,
        "acme",
        ["https://example.com/a"],
        {"title": "h1.title"},
        content_field="title",
        id_field="id",
        vector_index=1,
        chunk_size=200,
        overlap=20,
        partition=None,
    )


def test_crawl_and_train_accepts_optional_fields():
    fake_ds_client = MagicMock()

    with (
        patch("talkingdb_st.api.crawl.DSClient", return_value=fake_ds_client),
        patch(
            "talkingdb_st.api.crawl.crawl_and_index",
            return_value={"pages_crawled": 0, "chunks_indexed": 0, "failures": []},
        ) as crawl_and_index,
    ):
        response = client.post(
            "/api/namespaces/acme/crawl",
            json={
                "urls": [],
                "selectors": {},
                "content_field": "title",
                "id_field": "doc_id",
                "vector_index": 2,
                "chunk_size": 100,
                "overlap": 10,
                "partition": "tenant-1",
            },
        )

    assert response.status_code == 200
    _, kwargs = crawl_and_index.call_args
    assert kwargs["id_field"] == "doc_id"
    assert kwargs["vector_index"] == 2
    assert kwargs["chunk_size"] == 100
    assert kwargs["overlap"] == 10
    assert kwargs["partition"] == "tenant-1"


def test_crawl_and_train_requires_content_field():
    response = client.post(
        "/api/namespaces/acme/crawl",
        json={"urls": [], "selectors": {}},
    )

    assert response.status_code == 422


def test_discover_sitemap_delegates_to_service():
    with patch(
        "talkingdb_st.api.crawl.discover_urls_from_sitemap",
        return_value=["https://example.com/a", "https://example.com/b"],
    ) as discover:
        response = client.post(
            "/api/sitemap/discover",
            json={"sitemap_url": "https://example.com/sitemap.xml"},
        )

    assert response.status_code == 200
    assert response.json() == ["https://example.com/a", "https://example.com/b"]
    discover.assert_called_once_with("https://example.com/sitemap.xml")


def test_discover_sitemap_requires_sitemap_url():
    response = client.post("/api/sitemap/discover", json={})

    assert response.status_code == 422
