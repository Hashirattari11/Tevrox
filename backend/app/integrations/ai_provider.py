from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Contract for a future swappable AI provider; no API calls are made here."""

    @abstractmethod
    async def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Analyze a caller-provided payload and return a structured result."""
