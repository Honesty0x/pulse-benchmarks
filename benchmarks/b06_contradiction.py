"""Benchmark 06: Contradiction — Does the system detect conflicting facts?"""


def run(adapter, config: dict = None) -> dict:
    """Test if the system handles contradictory knowledge intelligently."""
    adapter.clear()

    # Store baseline facts
    baselines = [
        ("The API uses REST with JSON payloads.", "api"),
        ("The database is PostgreSQL 14 on RDS.", "database"),
        ("Deployments go through GitHub Actions CI.", "deployment"),
        ("The auth system uses JWT with RS256 signing.", "auth"),
        ("The cache layer is Redis 7 with 1-hour TTL.", "cache"),
    ]
    for content, domain in baselines:
        adapter.save(content, {"domain": domain, "benchmark": "contradiction"})

    # Store contradictions
    contradictions = [
        ("The API was migrated to GraphQL, REST is deprecated.", "api"),
        ("The database was upgraded to PostgreSQL 16.", "database"),
        ("Deployments now use ArgoCD, GitHub Actions was removed.", "deployment"),
        ("Auth switched to OAuth 2.0 with PKCE, JWT is no longer used.", "auth"),
        ("Redis was replaced by Memcached with 30-minute TTL.", "cache"),
    ]
    for content, domain in contradictions:
        adapter.save(content, {"domain": domain, "benchmark": "contradiction"})

    total = adapter.count()

    # Test: when searching, does the system prefer the newer fact?
    newer_wins = 0
    stale_returned = 0
    tests = [
        ("API protocol", "GraphQL", "REST"),
        ("database version", "16", "14"),
        ("deployment CI tool", "ArgoCD", "GitHub Actions"),
        ("authentication method", "OAuth", "JWT"),
        ("cache system", "Memcached", "Redis"),
    ]
    for query, new_marker, old_marker in tests:
        results = adapter.search(query, top_k=3)
        if not results:
            continue
        top_content = results[0].get("content", "")
        if new_marker in top_content:
            newer_wins += 1
        if old_marker in top_content:
            stale_returned += 1

    # Test: are both versions stored, or did the system deduplicate?
    both_stored = 0
    for query, new_marker, old_marker in tests:
        results = adapter.search(query, top_k=5)
        contents = " ".join(r.get("content", "") for r in results)
        if new_marker in contents and old_marker in contents:
            both_stored += 1

    freshness_score = newer_wins / len(tests)
    staleness_penalty = stale_returned / len(tests)
    overall = freshness_score * (1.0 - staleness_penalty * 0.5)

    adapter.clear()

    return {
        "benchmark": "contradiction",
        "total_items": total,
        "baseline_facts": len(baselines),
        "contradictions_added": len(contradictions),
        "newer_fact_ranked_first": newer_wins,
        "stale_fact_ranked_first": stale_returned,
        "both_versions_in_results": both_stored,
        "freshness_score": round(freshness_score, 3),
        "score": round(overall, 3),
    }
