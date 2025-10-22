from __future__ import annotations

import re
import unicodedata


_slugify_pattern = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = _slugify_pattern.sub("-", value).strip("-")
    return value or "client"
