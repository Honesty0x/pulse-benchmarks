"""Benchmark 07: Drift — Does knowledge quality degrade over time?"""
import time


def run(adapter, config: dict = None) -> dict:
    """Test if retrieval quality holds up as the knowledge base grows."""
    adapter.clear()

    # Phase 1: Store 10 high-quality seed items
    seeds = [
        "The authentication service uses OAuth 2.0 with PKCE flow for all mobile clients.",
        "Database migrations must be run before deployment using alembic upgrade head.",
        "The rate limiter allows 100 requests per minute per API key with sliding window.",
        "Error logs are shipped to Datadog via the fluentd sidecar container.",
        "The payment webhook endpoint must return 200 within 5 seconds or Stripe retries.",
        "Feature flags are managed through LaunchDarkly with a 30-second sync interval.",
        "The search index rebuilds nightly at 3 AM UTC via a Kubernetes CronJob.",
        "Session tokens expire after 24 hours and refresh tokens after 30 days.",
        "The CDN cache purge takes up to 15 minutes to propagate globally.",
        "Worker processes are limited to 512MB memory via cgroup constraints.",
    ]
    for s in seeds:
        adapter.save(s, {"phase": "seed", "benchmark": "drift"})

    # Measure baseline search quality on seeds
    baseline_hits = 0
    queries = ["OAuth authentication mobile", "database migration alembic",
               "rate limiter API requests", "error logs Datadog",
               "payment webhook Stripe timeout"]
    for q in queries:
        results = adapter.search(q, top_k=3)
        if any(len(r.get("content", "")) > 40 for r in results):
            baseline_hits += 1
    baseline_score = baseline_hits / len(queries)

    # Phase 2: Flood with 50 medium-quality items (dilute the corpus)
    for i in range(50):
        adapter.save(
            f"Development note {i}: discussed refactoring the {['auth', 'payment', 'search', 'logging', 'deploy'][i % 5]} "
            f"module to improve {'performance' if i % 2 == 0 else 'maintainability'}. "
            f"Decision pending review from the team lead.",
            {"phase": "dilution", "benchmark": "drift"}
        )

    # Phase 3: Re-measure search quality on the SAME seed queries
    post_dilution_hits = 0
    for q in queries:
        results = adapter.search(q, top_k=3)
        if any(len(r.get("content", "")) > 40 for r in results):
            post_dilution_hits += 1
    diluted_score = post_dilution_hits / len(queries)

    # Phase 4: Add 20 more noisy items
    for i in range(20):
        adapter.save(f"Meeting note: sync with team about sprint planning for Q2 item {i}.",
                     {"phase": "noise", "benchmark": "drift"})

    # Phase 5: Final measurement
    final_hits = 0
    for q in queries:
        results = adapter.search(q, top_k=3)
        if any(len(r.get("content", "")) > 40 for r in results):
            final_hits += 1
    final_score = final_hits / len(queries)

    total = adapter.count()
    drift = baseline_score - final_score

    adapter.clear()

    return {
        "benchmark": "drift",
        "total_items": total,
        "seed_items": len(seeds),
        "dilution_items": 50,
        "noise_items": 20,
        "baseline_score": round(baseline_score, 3),
        "post_dilution_score": round(diluted_score, 3),
        "final_score": round(final_score, 3),
        "drift_amount": round(drift, 3),
        "score": round(final_score, 3),
    }
