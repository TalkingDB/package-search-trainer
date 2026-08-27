import requests

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_USER_AGENT = "talkingdb-search-trainer/1.0"


class FetchError(Exception):
    """The page could not be fetched (network error or non-2xx status)."""


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    """Fetch a URL's raw HTML. Raises FetchError on any failure - callers
    doing a bulk crawl are expected to catch this per-URL and continue."""

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT},
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FetchError(f"failed to fetch {url}: {exc}") from exc

    return response.text
