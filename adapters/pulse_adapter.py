"""PULSE OS adapter for benchmarks.

Connects to PULSE's SQLite brain via brain_db and brain_search.
Requires PULSE to be installed or the repo to be on sys.path.
"""
import sys
from pathlib import Path

# Auto-detect PULSE repo location
_PULSE_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent / "PULSE",
    Path(__file__).resolve().parent.parent.parent / "babel_bot" / "PULSE",
    Path.home() / "Documents" / "projects" / "babel_bot" / "PULSE",
]
for _p in _PULSE_CANDIDATES:
    if (_p / "pulse" / "core" / "brain_db.py").exists():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

from adapters.base_adapter import BaseAdapter


class PulseAdapter(BaseAdapter):
    """Adapter for PULSE OS brain (SQLite-backed)."""

    def __init__(self, table: str = "lessons"):
        self._table = table
        self._test_prefix = "BENCH_"

    def save(self, content: str, metadata: dict = None) -> str:
        from pulse.core.brain_db import insert_knowledge
        metadata = metadata or {}
        data = {
            "content": content,
            "domain": metadata.get("domain", "benchmark"),
            "agent": metadata.get("agent", "benchmark_runner"),
            "confidence": metadata.get("confidence", 0.6),
            "salience": metadata.get("salience", 2.0),
            "source_type": "CONFIRMED",
        }
        result = insert_knowledge(self._table, data)
        return result if isinstance(result, str) else ""

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        from pulse.brain.brain_search import brain_search
        results = brain_search(query, max_per_source=top_k)
        hits = []
        for source_hits in results.get("results", {}).values():
            if isinstance(source_hits, list):
                for h in source_hits:
                    hits.append({
                        "content": h.get("text", h.get("title", "")),
                        "score": h.get("salience", 0) * h.get("confidence", 0.5),
                        "id": h.get("id", ""),
                    })
        hits.sort(key=lambda x: x["score"], reverse=True)
        return hits[:top_k]

    def delete(self, item_id: str) -> bool:
        try:
            from pulse.core.brain_db import get_conn
            conn = get_conn()
            conn.execute(f"DELETE FROM {self._table} WHERE id = ?", (item_id,))
            conn.commit()
            return True
        except Exception:
            return False

    def count(self) -> int:
        try:
            from pulse.core.brain_db import get_conn
            conn = get_conn()
            return conn.execute(f"SELECT COUNT(*) FROM {self._table}").fetchone()[0]
        except Exception:
            return 0

    def clear(self) -> None:
        """Clear only benchmark items (don't wipe real brain data)."""
        try:
            from pulse.core.brain_db import get_conn
            conn = get_conn()
            conn.execute(
                f"DELETE FROM {self._table} WHERE domain = 'benchmark'"
            )
            conn.commit()
        except Exception:
            pass

    def get_info(self) -> dict:
        try:
            import importlib.metadata
            version = importlib.metadata.version("pulse-os")
        except Exception:
            version = "dev"
        return {
            "system": "PULSE OS",
            "version": version,
            "backend": "SQLite + FTS5 + ONNX embeddings",
        }
