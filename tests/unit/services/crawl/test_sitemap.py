import responses

from talkingdb_st.services.crawl.sitemap import (
    SitemapParseError,
    discover_urls_from_sitemap,
)

VALID_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/one</loc></url>
  <url><loc>https://example.com/two</loc></url>
</urlset>
"""


@responses.activate
def test_discover_urls_from_sitemap_returns_every_loc():
    responses.add(
        responses.GET,
        "https://example.com/sitemap.xml",
        body=VALID_SITEMAP,
        status=200,
    )

    urls = discover_urls_from_sitemap("https://example.com/sitemap.xml")

    assert urls == ["https://example.com/one", "https://example.com/two"]


@responses.activate
def test_discover_urls_from_sitemap_returns_empty_list_for_empty_urlset():
    responses.add(
        responses.GET,
        "https://example.com/sitemap.xml",
        body='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
        status=200,
    )

    urls = discover_urls_from_sitemap("https://example.com/sitemap.xml")

    assert urls == []


@responses.activate
def test_discover_urls_from_sitemap_raises_on_invalid_xml():
    responses.add(
        responses.GET,
        "https://example.com/sitemap.xml",
        body="not xml at all <<<",
        status=200,
    )

    try:
        discover_urls_from_sitemap("https://example.com/sitemap.xml")
        assert False, "expected SitemapParseError"
    except SitemapParseError as exc:
        assert "https://example.com/sitemap.xml" in str(exc)
