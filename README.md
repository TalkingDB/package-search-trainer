# package-search-trainer

Generic crawl-and-train pipeline: fetches pages from configured seed URLs (or
a sitemap), extracts named fields via CSS selectors, chunks the content, and
pushes the result into `package-document-search` for vector and keyword
search.

This package is domain-agnostic TalkingDB infrastructure: it has no built-in
concept of "products," "ecommerce," a WooCommerce connector, or any specific
site. Every crawl is fully parameterized by the caller (seed URLs, CSS
selectors, which field to chunk); domain-specific crawl configs (e.g. an
ecommerce store's product-page selectors, its sitemap URL, its per-tenant
unit-tagging rules) belong to the `module-*` repo that consumes this package,
not to the package itself.

## Status

Core crawl pipeline (fetch, extract, chunk, sitemap discovery) and the
training orchestrator (composes `package-document-search`'s `DSClient`) are
implemented and tested. Pushing extracted structured data into an ontology is
a deliberately separate step: shape crawled fields into ontology nodes in the
caller and push them with `package-parse-tree`'s `PTClient` directly, since
that shaping is a domain-specific decision this package shouldn't make.

## Client

`talkingdb_st.client.STClient` gives callers a single interface that works
two ways, controlled by the `CLIENT_MODE` env var (defaults to `direct`):

- **DIRECT mode**: runs the crawl in-process and pushes into
  `package-document-search` via a `DSClient` it constructs itself (which
  respects its own `CLIENT_MODE`, so a fully single-process deployment of
  every package stays single-process).
- **API mode**: calls a deployed package-search-trainer service over HTTP.
  Set `CLIENT_MODE=api` and `ST_HOST` to the deployed base URL.

## Development

```
make sync MODE=git      # or MODE=local for editable base-tdb-* checkouts
poetry install
make test
make local               # run with hot reload
```

See `Makefile` for the full list of targets.
