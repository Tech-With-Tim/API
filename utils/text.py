def dedent(string: str) -> str:
    """Remove all leading spaces from `string`."""
    result = ""
    for line in string.splitlines(keepends=True):
        result += line.lstrip()
    return result
