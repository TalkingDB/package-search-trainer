from typing import Optional

from talkingdb_st.services.crawl.chunker import chunk_text
from talkingdb_st.services.crawl.extractor import extract_content
from talkingdb_st.services.crawl.fetcher import FetchError, fetch_page


def crawl_and_index(
    ds_client,
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
    """Crawl each URL, extract fields via CSS selectors, chunk the
    designated content field, and push the resulting chunks into
    package-document-search for both vector and keyword search.

    ``ds_client`` is a DSClient (or anything with the same
    train_vectors/train_keywords signatures) - this function has no
    knowledge of what's being crawled or what domain it belongs to,
    matching every other package in this porting effort. The target
    namespace's Milvus schema (created separately, before calling this)
    is assumed to be exactly (id, embedding) - any other extracted fields
    are only pushed to the keyword index, not to Milvus. A caller that
    wants additional fields available on vector search results needs a
    matching wider schema and to include those fields in ``bulk_data``
    itself; this v1 keeps the common case simple.

    Structured data extraction into an ontology (via package-parse-tree's
    PTClient) is a separate, deliberately un-composed step - shaping
    crawled fields into ontology nodes is a domain-specific decision that
    belongs in the caller (e.g. module-ecommerce-ai), not in this generic
    pipeline. Call PTClient.upsert_ontology_data directly for that.
    """

    ids: list[str] = []
    contents: list[str] = []
    keyword_docs: list[dict] = []
    failures: list[dict] = []

    for url in urls:
        try:
            html = fetch_page(url)
        except FetchError as exc:
            failures.append({"url": url, "error": str(exc)})
            continue

        fields = extract_content(html, selectors)
        content = fields.get(content_field, "")
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)

        for i, chunk in enumerate(chunks):
            doc_id = f"{url}#chunk{i}"
            ids.append(doc_id)
            contents.append(chunk)
            keyword_docs.append({**fields, content_field: chunk, id_field: doc_id})

    if ids:
        ds_client.train_vectors(
            namespace, [ids, contents], vector_index=vector_index, partition=partition
        )
        ds_client.train_keywords(
            namespace, keyword_docs, id_field=id_field, partition=partition
        )

    return {
        "pages_crawled": len(urls) - len(failures),
        "chunks_indexed": len(ids),
        "failures": failures,
    }
