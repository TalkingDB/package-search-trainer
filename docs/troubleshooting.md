# Troubleshooting

[Docs home](README.md) › Troubleshooting

| Symptom | Likely cause | Fix |
| :--- | :--- | :--- |
| `chunks_indexed` is 0 and nothing was trained | Every fetch failed, or the `content_field` selector matched nothing on every page | Check `failures`; open a page and test the selector in the browser console with `document.querySelectorAll("...")` |
| A field is always empty | The selector matches nothing, or the content is drawn by JavaScript after the page loads | Use a selector from the server's HTML (view source, not the live page) |
| `failures` lists timeouts | The site did not answer within 30 seconds | Retry later, or crawl fewer pages per call |
| `failures` lists 403 or 429 | The site blocks or rate limits the crawler | Ask for permission or an API; do not work around blocks |
| `ValueError: overlap must be smaller than chunk_size` | `overlap` is equal to or larger than `chunk_size` | Use a smaller overlap |
| Training fails with a Milvus schema or field count error | The namespace schema is not exactly `(id, embedding)` | Create the namespace with that two field schema, or build the bulk data yourself |
| Training fails because the namespace is not registered | The namespace was never created in package-document-search | Create it there first |
| Sitemap discovery returns `[]` | The URL is a sitemap index, or the XML uses another namespace | Call discovery once per child sitemap listed in the index |
| `SitemapParseError` | The response was not valid XML (for example an HTML error page) | Open the sitemap URL in a browser and check it |
| `ModuleNotFoundError` for `talkingdb_ds` or `talkingdb_pt` | The pinned packages are not installed | `make sync MODE=git && poetry install`, or `MODE=local` with sibling checkouts |

---

**Related:** [Architecture](architecture.md) · [Usage and examples](usage-and-examples.md) · [README](../README.md)
