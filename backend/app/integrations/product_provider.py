from abc import ABC, abstractmethod
from typing import Any


class ProductProvider(ABC):
    """Contract for a future swappable external product catalog."""

    @abstractmethod
    async def get_product(self, identifier: str) -> dict[str, Any] | None:
        """Return a product record when an implementation is added."""
