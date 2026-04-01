# PULSE Benchmarks

**Standard benchmarks for AI agent memory systems.**

Run these against any persistent memory system — PULSE, Mem0, LangChain Memory, Zep, Mengram, or your own — and get comparable, reproducible results.

## Why

Every AI memory product claims "persistent memory." None of them agree on what that means or how to measure it. These benchmarks define 7 concrete capabilities that a production memory system should have, and measure each one objectively.

## The 7 Benchmarks

| # | Benchmark | What it measures |
|---|---|---|
| 1 | **Retention** | Can the system recall knowledge after N sessions? |
| 2 | **Quality** | What percentage of stored knowledge is signal vs noise? |
| 3 | **Latency** | How fast is save + search (round-trip)? |
| 4 | **Consolidation** | Does old knowledge get merged, decayed, or just pile up? |
| 5 | **Multi-Agent** | Can 2+ agents share knowledge without conflicts? |
| 6 | **Contradiction** | Does the system detect conflicting facts? |
| 7 | **Drift** | Does knowledge quality degrade over time? |

## Quick Start

```bash
git clone https://github.com/Honesty0x/pulse-benchmarks
cd pulse-benchmarks

# Install
pip install -r requirements.txt

# Run all benchmarks against PULSE
python benchmarks/runner.py --adapter pulse

# Run against your own system
python benchmarks/runner.py --adapter custom --config your_adapter.py

# View results
cat results/latest.json
```

## Writing an Adapter

To benchmark your own memory system, implement the `BaseAdapter` interface:

```python
from adapters.base_adapter import BaseAdapter

class MyMemoryAdapter(BaseAdapter):
    def save(self, content: str, metadata: dict) -> str:
        """Store knowledge. Return item ID."""
        ...

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant knowledge. Return ranked results."""
        ...

    def delete(self, item_id: str) -> bool:
        """Delete a specific item."""
        ...

    def count(self) -> int:
        """Total items stored."""
        ...

    def clear(self) -> None:
        """Wipe all stored knowledge (for test isolation)."""
        ...
```

See `adapters/pulse_adapter.py` for a reference implementation.

## Results

| System | Retention | Quality | Latency | Consolidation | Multi-Agent | Contradiction | Drift | Overall |
|--------|-----------|---------|---------|---------------|-------------|---------------|-------|---------|
| **PULSE v10.59** | 0.800 | 0.143 | 0.921 | 0.333 | 1.000 | 0.000 | 1.000 | **0.600 (C)** |

PULSE v10.59 results: strong on latency (86ms round-trip), multi-agent (perfect cross-agent sharing), and drift resistance (zero degradation). Weak on contradiction ranking and synchronous dedup (consolidation runs async every 6h). Quality gate operates at the extraction layer, not the database layer — a known architectural gap being addressed in v10.60.

*Submit a PR with your system's results to appear in this table.*

## Methodology

Each benchmark runs in isolation with a clean state. See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for detailed scoring criteria.

## License

MIT License. Use freely. Benchmark everything.

## Contributing

PRs welcome for:
- New adapters (Mem0, Zep, LangChain, etc.)
- Additional benchmarks
- Bug fixes

Built by [PULSE OS](https://pulseos.dev) — cognitive infrastructure for AI agents.
