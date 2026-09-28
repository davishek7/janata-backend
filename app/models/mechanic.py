from .base import BaseDocument


class Mechanic(BaseDocument):
    full_name: str

    phone: str | None = None

    class Settings:
        name = "mechanics"
