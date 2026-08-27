import responses
from requests.exceptions import ConnectionError

from talkingdb_st.services.crawl.fetcher import (
    DEFAULT_USER_AGENT,
    FetchError,
    fetch_page,
)


@responses.activate
def test_fetch_page_returns_body_text():
    responses.add(
        responses.GET,
        "https://example.com/page",
        body="<html>hello</html>",
        status=200,
    )

    result = fetch_page("https://example.com/page")

    assert result == "<html>hello</html>"
    assert responses.calls[0].request.headers["User-Agent"] == DEFAULT_USER_AGENT


@responses.activate
def test_fetch_page_raises_fetch_error_on_non_2xx():
    responses.add(
        responses.GET,
        "https://example.com/missing",
        status=404,
    )

    try:
        fetch_page("https://example.com/missing")
        assert False, "expected FetchError"
    except FetchError as exc:
        assert "https://example.com/missing" in str(exc)


@responses.activate
def test_fetch_page_raises_fetch_error_on_connection_failure():
    responses.add(
        responses.GET,
        "https://unreachable.example.com/",
        body=ConnectionError("connection refused"),
    )

    try:
        fetch_page("https://unreachable.example.com/")
        assert False, "expected FetchError"
    except FetchError:
        pass


@responses.activate
def test_fetch_page_passes_custom_timeout():
    responses.add(
        responses.GET,
        "https://example.com/slow",
        body="ok",
        status=200,
    )

    result = fetch_page("https://example.com/slow", timeout=5)

    assert result == "ok"
