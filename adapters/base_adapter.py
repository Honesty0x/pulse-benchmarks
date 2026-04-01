"""Base adapter interface for benchmarking any AI memory system."""
from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """Implement this interface to benchmark your memory system.

    Each method maps to a core memory operation. The benchmark suite
    calls these methods — your adapter translates them to your system's API.
    """

    @abstractmethod
    def save(self, content: str, metadata: dict = None) -> str:
        """Store a piece of knowledge. Return a unique item ID.

        Args:
            content: The knowledge text to store.
            metadata: Optional dict with domain, source_type, confidence, etc.

        Returns:
            A string ID that can be used to retrieve or delete this item.
        """

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant knowledge. Return ranked results.

        Args:
            query: Natural language search query.
            top_k: Maximum number of results to return.

        Returns:
            List of dicts, each with at minimum:
                - "content": str (the stored text)
                - "score": float (relevance score, higher = better)
                - "id": str (item ID)
        """

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """Delete a specific item by ID. Return True if deleted."""

    @abstractmethod
    def count(self) -> int:
        """Return total number of items currently stored."""

    @abstractmethod
    def clear(self) -> None:
        """Wipe ALL stored knowledge. Used for test isolation."""

    def save_batch(self, items: list[dict]) -> list[str]:
        """Store multiple items. Default: sequential saves.

        Override for systems with native batch support.
        """
        ids = []
        for item in items:
            item_id = self.save(item["content"], item.get("metadata"))
            ids.append(item_id)
        return ids

    def get_info(self) -> dict:
        """Return system metadata for the results report."""
        return {
            "system": self.__class__.__name__,
            "version": "unknown",
        }
