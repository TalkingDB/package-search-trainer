from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from talkingdb.models.api.mode import ClientMode

from talkingdb_st.client import STClient


def direct_config():
    return SimpleNamespace(
        CLIENT_MODE=ClientMode.DIRECT, API_TIMEOUT=30, TDB_API_KEY=None
    )


def api_config(api_key=None):
    return SimpleNamespace(
        CLIENT_MODE=ClientMode.API, API_TIMEOUT=30, TDB_API_KEY=api_key
    )


class TestDirectMode:
    def test_crawl_and_train_composes_its_own_ds_client_and_orchestrator(self):
        client = STClient(config=direct_config())
        fake_ds_client = MagicMock()

        with (
            patch(
                "talkingdb_ds.client.DSClient", return_value=fake_ds_client
            ) as ds_cls,
            patch(
                "talkingdb_st.services.train.orchestrator.crawl_and_index",
                return_value={"pages_crawled": 1, "chunks_indexed": 3, "failures": []},
            ) as crawl_and_index,
        ):
            result = client.crawl_and_train(
                "acme",
                ["https://example.com/a"],
                {"title": "h1.title"},
                content_field="title",
            )

        assert result == {"pages_crawled": 1, "chunks_indexed": 3, "failures": []}
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

    def test_discover_sitemap_calls_service_directly(self):
        client = STClient(config=direct_config())

        with patch(
            "talkingdb_st.services.crawl.sitemap.discover_urls_from_sitemap",
            return_value=["https://example.com/a"],
        ) as discover:
            result = client.discover_sitemap("https://example.com/sitemap.xml")

        assert result == ["https://example.com/a"]
        discover.assert_called_once_with("https://example.com/sitemap.xml")


class TestApiMode:
    def test_requires_st_host(self):
        with pytest.raises(ValueError, match="ST_HOST"):
            STClient(config=api_config())

    def test_crawl_and_train_posts_to_configured_host(self, monkeypatch):
        monkeypatch.setenv("ST_HOST", "http://st.internal")
        client = STClient(config=api_config(api_key="secret"))

        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "pages_crawled": 1,
            "chunks_indexed": 1,
            "failures": [],
        }
        client.session.post = MagicMock(return_value=fake_response)

        result = client.crawl_and_train(
            "acme",
            ["https://example.com/a"],
            {"title": "h1.title"},
            content_field="title",
        )

        assert result == {"pages_crawled": 1, "chunks_indexed": 1, "failures": []}
        client.session.post.assert_called_once_with(
            "http://st.internal/api/namespaces/acme/crawl",
            json={
                "urls": ["https://example.com/a"],
                "selectors": {"title": "h1.title"},
                "content_field": "title",
                "id_field": "id",
                "vector_index": 1,
                "chunk_size": 200,
                "overlap": 20,
                "partition": None,
            },
            timeout=30,
        )
        assert client.session.headers["Authorization"] == "Bearer secret"

    def test_discover_sitemap_posts_to_configured_host(self, monkeypatch):
        monkeypatch.setenv("ST_HOST", "http://st.internal")
        client = STClient(config=api_config())

        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = ["https://example.com/a"]
        client.session.post = MagicMock(return_value=fake_response)

        result = client.discover_sitemap("https://example.com/sitemap.xml")

        assert result == ["https://example.com/a"]
        client.session.post.assert_called_once_with(
            "http://st.internal/api/sitemap/discover",
            json={"sitemap_url": "https://example.com/sitemap.xml"},
            timeout=30,
        )
