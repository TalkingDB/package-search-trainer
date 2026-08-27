from talkingdb_st.services.crawl.extractor import extract_content, extract_links

HTML = """
<html>
  <body>
    <h1 class="entry-title">Hello World</h1>
    <div class="entry-content">Some <b>body</b> text</div>
    <a href="/one">One</a>
    <a href="/two">Two</a>
    <a>No href</a>
  </body>
</html>
"""


def test_extract_content_pulls_named_fields_via_css_selectors():
    fields = extract_content(
        HTML, {"title": "h1.entry-title", "body": "div.entry-content"}
    )

    assert fields == {"title": "Hello World", "body": "Some body text"}


def test_extract_content_returns_empty_string_for_no_match():
    fields = extract_content(HTML, {"missing": "div.does-not-exist"})

    assert fields == {"missing": ""}


def test_extract_content_joins_multiple_matches():
    html = "<div class='item'>a</div><div class='item'>b</div>"

    fields = extract_content(html, {"items": "div.item"})

    assert fields == {"items": "a b"}


def test_extract_links_defaults_to_every_href():
    links = extract_links(HTML)

    assert links == ["/one", "/two"]


def test_extract_links_respects_custom_selector():
    links = extract_links(HTML, selector="a[href='/one']")

    assert links == ["/one"]
