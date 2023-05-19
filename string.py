from re import compile
from typing import Dict

RE_SNAKE_PATTERN = compile(r"(?<!^)(?=[A-Z])")

CACHE: Dict[str, str] = {}

def to_snake_case(name: str) -> str:
    if name in CACHE:
        return CACHE[name]

    sc: str = RE_SNAKE_PATTERN.sub("_", name).lower()
    CACHE[name] = sc
    return sc
