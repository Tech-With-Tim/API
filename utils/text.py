from urllib.parse import urlparse, parse_qs


def get_query(url: str) -> dict:
    """Parses the url provided and returns a dict of querystring arguments."""
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)


def dedent(string: str) -> str:
    """Remove all leading spaces from `string`."""
    result = ""
    for line in string.splitlines(keepends=True):
        result += line.lstrip()
    return result
