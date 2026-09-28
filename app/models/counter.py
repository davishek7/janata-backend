from .base import BaseDocument


class Counter(BaseDocument):
    key: str
    value: int = 0

    class Settings:
        name = "counters"
