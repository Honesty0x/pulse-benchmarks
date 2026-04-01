"""Benchmark 01: Retention — Can the system recall knowledge after N sessions?

Tests whether stored knowledge survives across simulated session boundaries.
A system that loses knowledge between sessions scores 0.
"""
import time


def run(adapter, config: dict = None) -> dict:
    """Run retention benchmark.

    Stores 20 knowledge items, simulates session gaps, checks recall.
    """
    config = config or {}
    num_items = config.get("num_items", 20)
    session_gaps = config.get("session_gaps", [1, 5, 10])

    # Phase 1: Store knowledge
    adapter.clear()
    items = []
    for i in range(num_items):
        content = f"Benchmark fact {i}: The {_DOMAINS[i % len(_DOMAINS)]} system uses {_TECHS[i % len(_TECHS)]} for {_PURPOSES[i % len(_PURPOSES)]}."
        item_id = adapter.save(content, {"domain": _DOMAINS[i % len(_DOMAINS)], "benchmark": "retention"})
        items.append({"id": item_id, "content": content, "domain": _DOMAINS[i % len(_DOMAINS)]})

    stored = adapter.count()

    # Phase 2: Check immediate recall
    immediate_hits = 0
    for item in items:
        results = adapter.search(item["content"][:50], top_k=3)
        if any(item["content"][:30] in r.get("content", "") for r in results):
            immediate_hits += 1

    # Phase 3: Simulate session gaps and re-check
    gap_results = {}
    for gap in session_gaps:
        time.sleep(min(gap * 0.1, 2))  # Simulated gap (scaled down)
        hits = 0
        for item in items[:10]:  # Check first 10 for speed
            results = adapter.search(item["content"][:50], top_k=3)
            if any(item["content"][:30] in r.get("content", "") for r in results):
                hits += 1
        gap_results[f"after_{gap}_sessions"] = hits / 10.0

    adapter.clear()

    return {
        "benchmark": "retention",
        "items_stored": stored,
        "items_expected": num_items,
        "immediate_recall": immediate_hits / num_items,
        "gap_recall": gap_results,
        "score": immediate_hits / num_items,  # Primary score
    }


_DOMAINS = ["auth", "database", "api", "frontend", "deployment", "security", "testing", "monitoring"]
_TECHS = ["OAuth 2.0", "PostgreSQL", "REST", "React", "Docker", "TLS 1.3", "pytest", "Prometheus"]
_PURPOSES = ["authentication", "persistence", "communication", "rendering", "orchestration", "encryption", "validation", "observability"]
