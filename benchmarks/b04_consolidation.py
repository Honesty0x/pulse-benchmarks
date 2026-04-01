"""Benchmark 04: Consolidation — Does old knowledge get merged, decayed, or just pile up?"""
import time


def run(adapter, config: dict = None) -> dict:
    """Test if the system consolidates redundant/stale knowledge."""
    adapter.clear()

    # Phase 1: Store 5 near-duplicate items (same fact, different wording)
    duplicates = [
        "The API server runs on port 8080 in production.",
        "Production API is served on port 8080.",
        "Port 8080 is used for the production API server.",
        "The prod API runs on port 8080.",
        "In production, the API server listens on port 8080.",
    ]
    for d in duplicates:
        adapter.save(d, {"domain": "deployment", "benchmark": "consolidation"})

    count_after_dupes = adapter.count()

    # Phase 2: Store contradictory knowledge
    adapter.save("The database uses PostgreSQL 14.", {"domain": "database", "benchmark": "consolidation"})
    time.sleep(0.5)
    adapter.save("The database was migrated to PostgreSQL 16.", {"domain": "database", "benchmark": "consolidation"})

    # Phase 3: Store stale knowledge then update
    adapter.save("The deploy script is at scripts/deploy.sh", {"domain": "deployment", "benchmark": "consolidation"})
    time.sleep(0.5)
    adapter.save("The deploy script was moved to ci/deploy.yaml", {"domain": "deployment", "benchmark": "consolidation"})

    count_total = adapter.count()

    # Check: does searching for "API port" return 1 consolidated answer or 5?
    port_results = adapter.search("API server port production", top_k=10)
    port_hits = len([r for r in port_results if "8080" in r.get("content", "")])

    # Check: does searching for "database version" return the latest?
    db_results = adapter.search("database PostgreSQL version", top_k=3)
    has_latest = any("16" in r.get("content", "") for r in db_results)
    has_stale = any("14" in r.get("content", "") for r in db_results[:1])  # Is stale ranked first?

    # Check: does searching for "deploy script" return the latest?
    deploy_results = adapter.search("deploy script location", top_k=3)
    has_new_path = any("deploy.yaml" in r.get("content", "") for r in deploy_results)

    # Scoring
    dedup_score = 1.0 if port_hits <= 2 else (0.5 if port_hits <= 3 else 0.0)
    freshness_score = 1.0 if (has_latest and not has_stale) else (0.5 if has_latest else 0.0)
    update_score = 1.0 if has_new_path else 0.0
    overall = (dedup_score + freshness_score + update_score) / 3.0

    adapter.clear()

    return {
        "benchmark": "consolidation",
        "duplicates_stored": count_after_dupes,
        "duplicates_submitted": len(duplicates),
        "dedup_ratio": round(count_after_dupes / len(duplicates), 2),
        "port_hits_in_search": port_hits,
        "latest_db_version_ranked_first": has_latest and not has_stale,
        "updated_path_found": has_new_path,
        "total_items": count_total,
        "score": round(overall, 3),
    }
