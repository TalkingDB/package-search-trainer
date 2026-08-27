from bs4 import BeautifulSoup


def extract_content(html: str, selectors: dict[str, str]) -> dict[str, str]:
    """Extract named fields from HTML via CSS selectors.

    ``selectors`` maps an arbitrary field name to a CSS selector, e.g.
    ``{"title": "h1.entry-title", "body": "div.entry-content"}``. A
    selector that matches nothing yields an empty string for that field
    rather than raising - a page missing one optional field shouldn't
    abort the whole crawl.

    Generic by design: this has no knowledge of what the fields mean or
    what site is being crawled. Domain-specific selector configs (e.g. an
    ecommerce product page's title/price/description selectors) are
    supplied by the caller, not hardcoded here.
    """

    soup = BeautifulSoup(html, "lxml")
    fields: dict[str, str] = {}

    for field_name, selector in selectors.items():
        matches = soup.select(selector)
        text = " ".join(m.get_text(separator=" ", strip=True) for m in matches)
        fields[field_name] = text

    return fields


def extract_links(html: str, selector: str = "a[href]") -> list[str]:
    """Extract hrefs matching a CSS selector - defaults to every link on
    the page. Used for simple crawl-frontier discovery (e.g. a listing
    page linking to individual item pages)."""

    soup = BeautifulSoup(html, "lxml")
    return [a["href"] for a in soup.select(selector) if a.get("href")]
