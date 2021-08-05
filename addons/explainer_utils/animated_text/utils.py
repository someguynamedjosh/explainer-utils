import string


def count_parts(text: str) -> int:
    fmt = string.Formatter()
    p = list(fmt.parse(text))
    return len([e for e in p if e[2] is not None])


def split_parts(text: str):
    fmt = string.Formatter()
    p = list(fmt.parse(text))
    return [(e[0], e[2]) for e in p]
