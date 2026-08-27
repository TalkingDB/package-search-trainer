from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
from talkingdb_ds.client import DSClient

from talkingdb_st.services.crawl.sitemap import discover_urls_from_sitemap
from talkingdb_st.services.train.orchestrator import crawl_and_index

router = APIRouter(prefix="/api/namespaces/{namespace}", tags=["Crawl & Train"])
sitemap_router = APIRouter(prefix="/api/sitemap", tags=["Crawl & Train"])


class CrawlTrainRequest(BaseModel):
    urls: list[str]
    selectors: dict[str, str]
    content_field: str
    id_field: str = "id"
    vector_index: int = 1
    chunk_size: int = 200
    overlap: int = 20
    partition: Optional[str] = None


class SitemapDiscoverRequest(BaseModel):
    sitemap_url: str


@router.post("/crawl")
def crawl_and_train(namespace: str, request: CrawlTrainRequest) -> dict:
    ds_client = DSClient()
    return crawl_and_index(
        ds_client,
        namespace,
        request.urls,
        request.selectors,
        content_field=request.content_field,
        id_field=request.id_field,
        vector_index=request.vector_index,
        chunk_size=request.chunk_size,
        overlap=request.overlap,
        partition=request.partition,
    )


@sitemap_router.post("/discover")
def discover_sitemap(request: SitemapDiscoverRequest) -> list[str]:
    return discover_urls_from_sitemap(request.sitemap_url)
