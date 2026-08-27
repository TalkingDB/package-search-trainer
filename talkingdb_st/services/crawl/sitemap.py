from xml.etree import ElementTree

from talkingdb_st.services.crawl.fetcher import fetch_page

_SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class SitemapParseError(Exception):
    pass


def discover_urls_from_sitemap(sitemap_url: str) -> list[str]:
    """Fetch a standard XML sitemap and return every <loc> URL in it.

    Handles a plain urlset sitemap. A sitemap index (a sitemap of
    sitemaps) is not recursed into automatically - callers needing that
    can call this once per child sitemap URL.
    """

    xml = fetch_page(sitemap_url)

    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise SitemapParseError(f"invalid sitemap XML at {sitemap_url}: {exc}") from exc

    return [
        loc.text.strip()
        for loc in root.findall(".//sm:url/sm:loc", _SITEMAP_NS)
        if loc.text
    ]
