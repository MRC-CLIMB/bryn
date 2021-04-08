from . import hashids


class HashidsConverter:
    """Path converter for hashids"""

    regex = hashids.REGEX

    def to_python(self, value: str) -> int:
        return hashids.decode(value)

    def to_url(self, value: int) -> str:
        return hashids.encode(value)
