"""Benchmark 05: Multi-Agent — Can 2+ agents share knowledge without conflicts?"""


def run(adapter, config: dict = None) -> dict:
    """Test if knowledge from one agent is accessible to another."""
    adapter.clear()

    # Agent A saves knowledge
    agent_a_items = [
        "Agent A discovered: the auth service requires a 30-second token refresh interval.",
        "Agent A learned: the CI pipeline fails silently when the Docker cache exceeds 2GB.",
        "Agent A confirmed: the staging database is on db-staging.internal port 5432.",
    ]
    for item in agent_a_items:
        adapter.save(item, {"agent": "agent_a", "benchmark": "multi_agent"})

    # Agent B saves knowledge (some overlapping, some unique)
    agent_b_items = [
        "Agent B found: token refresh should happen every 30 seconds to avoid 401 errors.",
        "Agent B noted: the monitoring dashboard uses Grafana at grafana.internal:3000.",
        "Agent B resolved: memory leak in the worker pool caused by unclosed database connections.",
    ]
    for item in agent_b_items:
        adapter.save(item, {"agent": "agent_b", "benchmark": "multi_agent"})

    total = adapter.count()

    # Can Agent B find Agent A's knowledge?
    cross_agent_hits = 0
    queries_from_b = [
        "auth token refresh interval",
        "CI pipeline Docker cache",
        "staging database connection",
    ]
    for q in queries_from_b:
        results = adapter.search(q, top_k=3)
        if any("Agent A" in r.get("content", "") for r in results):
            cross_agent_hits += 1

    # Can Agent A find Agent B's knowledge?
    queries_from_a = [
        "monitoring dashboard Grafana",
        "memory leak worker pool",
        "token refresh 401 errors",
    ]
    reverse_hits = 0
    for q in queries_from_a:
        results = adapter.search(q, top_k=3)
        if any("Agent B" in r.get("content", "") for r in results):
            reverse_hits += 1

    # Check overlap handling (both agents know about token refresh)
    overlap_results = adapter.search("token refresh interval", top_k=5)
    overlap_count = len([r for r in overlap_results if "refresh" in r.get("content", "").lower()])

    cross_score = cross_agent_hits / len(queries_from_b)
    reverse_score = reverse_hits / len(queries_from_a)
    overall = (cross_score + reverse_score) / 2.0

    adapter.clear()

    return {
        "benchmark": "multi_agent",
        "total_items": total,
        "agent_a_items": len(agent_a_items),
        "agent_b_items": len(agent_b_items),
        "b_finds_a_knowledge": cross_agent_hits,
        "a_finds_b_knowledge": reverse_hits,
        "cross_agent_score": round(cross_score, 3),
        "reverse_score": round(reverse_score, 3),
        "overlap_results": overlap_count,
        "score": round(overall, 3),
    }
