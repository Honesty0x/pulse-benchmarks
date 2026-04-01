"""Benchmark 03: Latency — How fast is save + search (round-trip)?"""
import time


def run(adapter, config: dict = None) -> dict:
    """Measure save and search latency across multiple operations."""
    adapter.clear()
    num_ops = 20

    # Warm up
    adapter.save("warmup item", {"benchmark": "latency"})
    adapter.search("warmup")

    # Measure save latency
    save_times = []
    for i in range(num_ops):
        content = f"Latency test item {i}: The deployment pipeline uses Docker with multi-stage builds for production optimization."
        t0 = time.perf_counter()
        adapter.save(content, {"benchmark": "latency", "index": i})
        save_times.append((time.perf_counter() - t0) * 1000)

    # Measure search latency
    search_times = []
    queries = ["deployment pipeline", "Docker builds", "production optimization",
               "multi-stage", "latency test", "deployment", "pipeline uses",
               "builds for production", "Docker", "optimization"]
    for q in queries[:num_ops]:
        t0 = time.perf_counter()
        adapter.search(q, top_k=5)
        search_times.append((time.perf_counter() - t0) * 1000)

    # Round-trip: save then immediately search
    roundtrip_times = []
    for i in range(5):
        content = f"Round-trip test {i}: unique marker {time.time()}"
        t0 = time.perf_counter()
        adapter.save(content, {"benchmark": "latency"})
        adapter.search(content[:30], top_k=1)
        roundtrip_times.append((time.perf_counter() - t0) * 1000)

    adapter.clear()

    return {
        "benchmark": "latency",
        "save_ms": {"min": round(min(save_times), 1), "max": round(max(save_times), 1),
                     "avg": round(sum(save_times) / len(save_times), 1)},
        "search_ms": {"min": round(min(search_times), 1), "max": round(max(search_times), 1),
                       "avg": round(sum(search_times) / len(search_times), 1)},
        "roundtrip_ms": {"min": round(min(roundtrip_times), 1), "max": round(max(roundtrip_times), 1),
                          "avg": round(sum(roundtrip_times) / len(roundtrip_times), 1)},
        "score": round(1.0 / (1.0 + sum(roundtrip_times) / len(roundtrip_times) / 1000), 3),
    }
