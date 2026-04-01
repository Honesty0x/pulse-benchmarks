"""Benchmark 02: Quality — What percentage of stored knowledge is signal vs noise?

Feeds a mix of high-quality knowledge and garbage into the system,
then checks if the system filters noise or stores everything blindly.
"""


def run(adapter, config: dict = None) -> dict:
    """Run quality benchmark.

    Stores 20 good items + 20 garbage items, checks what gets retained.
    """
    adapter.clear()

    good_items = [
        "The SQLite busy_timeout must be set to 60000ms to prevent lock convoy crashes with concurrent agents.",
        "OAuth 2.0 refresh tokens should be rotated on every use to prevent token replay attacks.",
        "React useEffect cleanup functions must cancel pending API calls to avoid state updates on unmounted components.",
        "PostgreSQL VACUUM ANALYZE should run weekly on tables with >10% dead tuple ratio.",
        "Docker multi-stage builds reduce image size by 60-80% by separating build and runtime dependencies.",
        "The FSRS-6 spaced repetition algorithm uses a power-law forgetting curve with 4 parameters.",
        "Python asyncio.gather with return_exceptions=True prevents one failed coroutine from canceling siblings.",
        "Git rebase --onto is safer than merge for moving feature branches when the base branch has been force-pushed.",
        "Nginx proxy_read_timeout defaults to 60s which causes 504 errors on long-running API endpoints.",
        "The BCM sliding threshold in synaptic plasticity prevents runaway excitation by raising the modification threshold.",
        "TLS 1.3 removed RSA key exchange, mandatory forward secrecy via ephemeral Diffie-Hellman.",
        "SQLite WAL mode allows concurrent readers during writes, essential for multi-agent architectures.",
        "Kubernetes liveness probes should check downstream dependencies, not just return 200 OK.",
        "The hippocampus consolidates episodic memories into semantic knowledge during slow-wave sleep.",
        "ONNX Runtime inference is 17x faster than PyTorch for sentence-transformers on CPU cold start.",
        "Redis SCAN is O(1) per call vs KEYS which is O(N) and blocks the entire server.",
        "Python dataclasses with frozen=True are hashable and can be used as dict keys or set members.",
        "GraphQL N+1 queries are solved by DataLoader batching, not by eager loading in the resolver.",
        "The CAP theorem proves you cannot have consistency, availability, and partition tolerance simultaneously.",
        "Webhook retry strategies should use exponential backoff with jitter to prevent thundering herd.",
    ]

    garbage_items = [
        "bro lets go",
        "ok",
        "| col1 | col2 | col3 |",
        "yeah sounds good",
        "lmao",
        "<task-notification>test</task-notification>",
        "...",
        "hmm let me think",
        "yo check this out",
        "nice nice nice",
        "idk maybe",
        "sure thing",
        "Loading weights: 100%",
        "```json\n{}\n```",
        "the the the",
        "asdf",
        "todo: fix later",
        "hey",
        "what do you think?",
        "right right right",
    ]

    # Store everything
    good_ids = []
    for item in good_items:
        gid = adapter.save(item, {"quality": "good", "benchmark": "quality"})
        good_ids.append(gid)

    garbage_ids = []
    for item in garbage_items:
        gid = adapter.save(item, {"quality": "garbage", "benchmark": "quality"})
        garbage_ids.append(gid)

    total_stored = adapter.count()
    good_stored = 0
    garbage_stored = 0

    # Check what survived
    for item in good_items:
        results = adapter.search(item[:40], top_k=1)
        if results and item[:20] in results[0].get("content", ""):
            good_stored += 1

    for item in garbage_items:
        results = adapter.search(item, top_k=1)
        if results and item in results[0].get("content", ""):
            garbage_stored += 1

    good_rate = good_stored / len(good_items)
    garbage_rate = garbage_stored / len(garbage_items)
    quality_score = good_rate * (1.0 - garbage_rate)

    adapter.clear()

    return {
        "benchmark": "quality",
        "good_items_submitted": len(good_items),
        "garbage_items_submitted": len(garbage_items),
        "good_retained": good_stored,
        "garbage_retained": garbage_stored,
        "good_retention_rate": round(good_rate, 3),
        "garbage_rejection_rate": round(1.0 - garbage_rate, 3),
        "score": round(quality_score, 3),
    }
