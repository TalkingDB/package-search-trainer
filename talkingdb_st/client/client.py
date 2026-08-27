import os
from typing import Any, Optional

import requests
from talkingdb.helpers.client import Config
from talkingdb.models.api.mode import ClientMode


class STClient:
    """Dual-mode client for package-search-trainer.

    In DIRECT mode (default), runs the crawl in-process and pushes results
    into package-document-search via a DSClient it constructs itself (which
    respects its own CLIENT_MODE - so a fully single-process deployment
    stays single-process, no network hop for either package). In API mode,
    calls a deployed package-search-trainer service over HTTP.

    ``ST_HOST`` is read locally rather than added to base-tdb-helpers'
    shared Config, matching PTClient/PT_HOST and DSClient/DS_HOST.
    """

    def __init__(self, config: Optional[Config] = None, headers: Optional[dict] = None):
        config = config or Config()
        self.mode = config.CLIENT_MODE
        self.timeout = config.API_TIMEOUT
        self.endpoint = os.getenv("ST_HOST")
        self.api_key = config.TDB_API_KEY

        self.session: Optional[requests.Session] = None
        if self.mode == ClientMode.API:
            if not self.endpoint:
                raise ValueError("ST_HOST is required in API mode")

            self.session = requests.Session()
            if self.api_key:
                self.session.headers["Authorization"] = f"Bearer {self.api_key}"
            if headers:
                self.session.headers.update(headers)

    def crawl_and_train(
        self,
        namespace: str,
        urls: list[str],
        selectors: dict[str, str],
        *,
        content_field: str,
        id_field: str = "id",
        vector_index: int = 1,
        chunk_size: int = 200,
        overlap: int = 20,
        partition: Optional[str] = None,
    ) -> dict:
        payload = {
            "urls": urls,
            "selectors": selectors,
            "content_field": content_field,
            "id_field": id_field,
            "vector_index": vector_index,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "partition": partition,
        }
        if self.mode == ClientMode.API:
            return self._post(f"/api/namespaces/{namespace}/crawl", payload)

        from talkingdb_ds.client import DSClient

        from talkingdb_st.services.train.orchestrator import crawl_and_index

        return crawl_and_index(
            DSClient(),
            namespace,
            urls,
            selectors,
            content_field=content_field,
            id_field=id_field,
            vector_index=vector_index,
            chunk_size=chunk_size,
            overlap=overlap,
            partition=partition,
        )

    def discover_sitemap(self, sitemap_url: str) -> list[str]:
        if self.mode == ClientMode.API:
            return self._post("/api/sitemap/discover", {"sitemap_url": sitemap_url})

        from talkingdb_st.services.crawl.sitemap import discover_urls_from_sitemap

        return discover_urls_from_sitemap(sitemap_url)

    # ------------------------------------------------------------- boundary
    def _post(self, path: str, json_body: Any) -> Any:
        response = self.session.post(
            f"{self.endpoint}{path}", json=json_body, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
