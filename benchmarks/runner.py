#!/usr/bin/env python3
"""
PULSE Benchmark Runner — Run all 7 benchmarks against any memory system.

Usage:
    python benchmarks/runner.py --adapter pulse
    python benchmarks/runner.py --adapter custom --config my_adapter.py
    python benchmarks/runner.py --list
"""
import argparse
import importlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

BENCHMARKS = [
    "b01_retention",
    "b02_quality",
    "b03_latency",
    "b04_consolidation",
    "b05_multi_agent",
    "b06_contradiction",
    "b07_drift",
]

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def load_adapter(name: str, config_path: str = None):
    """Load a memory system adapter by name."""
    if name == "pulse":
        from adapters.pulse_adapter import PulseAdapter
        return PulseAdapter()
    elif name == "custom" and config_path:
        spec = importlib.util.spec_from_file_location("custom_adapter", config_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        adapter_cls = None
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and hasattr(obj, "save") and hasattr(obj, "search") and attr != "BaseAdapter":
                adapter_cls = obj
                break
        if not adapter_cls:
            print("Error: no adapter class found in config file")
            sys.exit(1)
        return adapter_cls()
    else:
        print(f"Unknown adapter: {name}")
        print("Available: pulse, custom (with --config)")
        sys.exit(1)


def run_all(adapter, benchmarks=None):
    """Run selected benchmarks and return results."""
    benchmarks = benchmarks or BENCHMARKS
    results = {
        "system": adapter.get_info(),
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {},
        "overall_score": 0.0,
    }

    total_score = 0.0
    count = 0

    for bname in benchmarks:
        print(f"\n{'='*50}")
        print(f"  Running: {bname}")
        print(f"{'='*50}")
        try:
            mod = importlib.import_module(f"benchmarks.{bname}")
            t0 = time.perf_counter()
            result = mod.run(adapter)
            elapsed = (time.perf_counter() - t0) * 1000
            result["elapsed_ms"] = round(elapsed, 1)
            results["benchmarks"][bname] = result
            score = result.get("score", 0)
            total_score += score
            count += 1
            status = "PASS" if score >= 0.7 else ("PARTIAL" if score >= 0.4 else "FAIL")
            print(f"  Score: {score:.3f} [{status}] ({elapsed:.0f}ms)")
        except Exception as e:
            print(f"  ERROR: {e}")
            results["benchmarks"][bname] = {"error": str(e), "score": 0}
            count += 1

    results["overall_score"] = round(total_score / max(count, 1), 3)
    return results


def print_summary(results: dict):
    """Print a formatted summary of benchmark results."""
    print(f"\n{'='*60}")
    print(f"  BENCHMARK RESULTS — {results['system'].get('system', 'Unknown')}")
    print(f"{'='*60}")

    for bname, data in results.get("benchmarks", {}).items():
        score = data.get("score", 0)
        elapsed = data.get("elapsed_ms", 0)
        status = "PASS" if score >= 0.7 else ("PARTIAL" if score >= 0.4 else "FAIL")
        label = bname.replace("b0", "").replace("_", " ").title()
        print(f"  {label:25s} {score:.3f}  [{status}]  {elapsed:.0f}ms")

    print(f"{'='*60}")
    overall = results.get("overall_score", 0)
    grade = "A" if overall >= 0.9 else "B" if overall >= 0.7 else "C" if overall >= 0.5 else "D" if overall >= 0.3 else "F"
    print(f"  OVERALL: {overall:.3f} (Grade: {grade})")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="PULSE Benchmark Runner")
    parser.add_argument("--adapter", default="pulse", help="Adapter name (pulse, custom)")
    parser.add_argument("--config", help="Path to custom adapter file")
    parser.add_argument("--list", action="store_true", help="List available benchmarks")
    parser.add_argument("--only", help="Run specific benchmarks (comma-separated)")
    parser.add_argument("--output", help="Output file path (default: results/latest.json)")
    args = parser.parse_args()

    if args.list:
        print("Available benchmarks:")
        for b in BENCHMARKS:
            print(f"  {b}")
        return

    # Add parent dir to path for adapter imports
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    adapter = load_adapter(args.adapter, args.config)
    benchmarks = args.only.split(",") if args.only else None

    results = run_all(adapter, benchmarks)
    print_summary(results)

    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output) if args.output else RESULTS_DIR / "latest.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Also save a timestamped copy
    ts_path = RESULTS_DIR / f"{results['system'].get('system', 'unknown').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    ts_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
