# Benchmark Methodology

## Scoring

Each benchmark produces a score between 0.0 and 1.0:

- **>= 0.9** — Grade A (excellent)
- **>= 0.7** — Grade B (good)
- **>= 0.5** — Grade C (acceptable)
- **>= 0.3** — Grade D (needs improvement)
- **< 0.3** — Grade F (failing)

The overall score is the unweighted average of all 7 benchmarks.

## Benchmark Details

### 01 Retention
Stores 20 knowledge items, checks immediate recall, then checks recall after simulated session gaps. A system that retains 100% of stored knowledge scores 1.0.

### 02 Quality
Feeds 20 high-quality items and 20 garbage items. Measures what percentage of good items are retained and what percentage of garbage is rejected. Score = good_retention * (1 - garbage_retention).

### 03 Latency
Measures save, search, and round-trip latency across 20 operations. Score is inversely proportional to round-trip time: 1/(1 + avg_seconds).

### 04 Consolidation
Tests deduplication (5 near-duplicate items), freshness (contradictory updates), and update propagation. Each capability scored equally.

### 05 Multi-Agent
Two simulated agents store knowledge. Tests whether each agent can find the other's knowledge. Score = average of cross-agent retrieval rates.

### 06 Contradiction
Stores baseline facts then contradictory updates. Checks if the system ranks newer facts higher and detects conflicts.

### 07 Drift
Stores 10 seed items, floods with 70 dilution items, measures if seed retrieval quality degrades. Score = final retrieval rate on seed queries.

## Test Isolation

Every benchmark calls `adapter.clear()` before and after running. Benchmarks do not affect each other or production data. The PULSE adapter clears only items with `domain='benchmark'`.

## Reproducibility

Results are deterministic given the same adapter implementation. No randomness in test data. Run `python benchmarks/runner.py` twice and compare.
