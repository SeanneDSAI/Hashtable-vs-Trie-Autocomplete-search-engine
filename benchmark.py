"""
benchmark.py
------------
Experimental framework for the DSAA2 assignment.

Implements the three required experiments:

    A) Insertion time           – Hash Table  vs  Trie
    B) Exact search             – Hash Table  vs  Linear scan (list)
    C) Prefix search            – Trie        vs  Linear scan (list)

Every measurement uses time.perf_counter() and is repeated TRIALS times
(default 5) with the average reported, as required by the spec.

Tests run across multiple dataset sizes:
    [1000, 5000, 10000, 50000, 87585]
"""

import time
import statistics

from data_loader.data_loader import MovieDataLoader
from hash_table import HashTable
from trie.trie import Trie


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Dataset sizes to benchmark
DATASET_SIZES = [1_000, 5_000, 10_000, 50_000, 87_585]

#: Number of repeated runs per measurement (averages reported)
TRIALS = 5

#: Prefixes used in the prefix-search benchmark
TEST_PREFIXES = ["the", "star", "dark", "love", "bl"]


# ---------------------------------------------------------------------------
# Linear search baselines (for comparison)
# ---------------------------------------------------------------------------

def linear_search(movies: list, title: str):
    """O(n) sequential scan for an exact title match."""
    title = title.lower()
    for movie in movies:
        if movie["clean_title"] == title:
            return movie
    return None


def linear_prefix_search(movies: list, prefix: str) -> list:
    """O(n) sequential scan returning all movies whose title starts with prefix."""
    prefix = prefix.lower()
    return [m for m in movies if m["clean_title"].startswith(prefix)]


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------

def _time_it(func, *args, trials: int = TRIALS) -> float:
    """
    Run *func(*args)* TRIALS times.  Return mean elapsed time in milliseconds.

    Uses time.perf_counter() (highest-resolution monotonic clock available).
    """
    durations = []
    for _ in range(trials):
        start = time.perf_counter()
        func(*args)
        durations.append((time.perf_counter() - start) * 1000.0)   # ms
    return statistics.mean(durations)


# ---------------------------------------------------------------------------
# Experiment A – Insertion time
# ---------------------------------------------------------------------------

def benchmark_insertion(movies: list) -> dict:
    """
    Time how long it takes to build a HashTable and a Trie from *movies*.

    Returns
    -------
    {'hash_ms': float, 'trie_ms': float}
    """
    def build_hash():
        ht = HashTable()
        for m in movies:
            ht.insert(m)

    def build_trie():
        tr = Trie()
        for m in movies:
            tr.insert(m)

    return {
        "hash_ms": _time_it(build_hash),
        "trie_ms": _time_it(build_trie),
    }


# ---------------------------------------------------------------------------
# Experiment B – Exact search
# ---------------------------------------------------------------------------

def benchmark_exact_search(movies: list) -> dict:
    """
    Compare:
      - HashTable.search   (expected O(1))
      - linear_search      (expected O(n))

    A single representative query is timed TRIALS times; result returned
    in microseconds for readability.
    """
    # Build the hash table once
    ht = HashTable()
    for m in movies:
        ht.insert(m)

    # 10 query titles spread evenly across the dataset
    step = max(1, len(movies) // 10)
    queries = [movies[i]["clean_title"] for i in range(0, len(movies), step)][:10]

    def hash_run():
        for q in queries:
            ht.search(q)

    def linear_run():
        for q in queries:
            linear_search(movies, q)

    return {
        # mean ms for 10 queries → divide by 10 → convert ms→µs (×1000)
        "hash_us":   _time_it(hash_run)   * 1000.0 / len(queries),
        "linear_us": _time_it(linear_run) * 1000.0 / len(queries),
    }


# ---------------------------------------------------------------------------
# Experiment C – Prefix search
# ---------------------------------------------------------------------------

def benchmark_prefix_search(movies: list) -> dict:
    """
    Compare:
      - Trie.autocomplete       (expected O(k + m))
      - linear_prefix_search    (expected O(n))

    Returns mean time PER PREFIX QUERY in milliseconds.
    """
    # Build trie once
    tr = Trie()
    for m in movies:
        tr.insert(m)

    def trie_run():
        for p in TEST_PREFIXES:
            tr.autocomplete(p)

    def linear_run():
        for p in TEST_PREFIXES:
            linear_prefix_search(movies, p)

    return {
        "trie_ms":   _time_it(trie_run)   / len(TEST_PREFIXES),
        "linear_ms": _time_it(linear_run) / len(TEST_PREFIXES),
    }


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

def run_full_benchmark(csv_path: str) -> dict:
    """
    Execute all three benchmarks across every size in DATASET_SIZES.

    Returns
    -------
    dict with three keys: 'insertion', 'exact', 'prefix'.
    Each value is a list of dicts indexed by dataset size.
    """
    loader = MovieDataLoader(csv_path)

    insertion_rows = []
    exact_rows     = []
    prefix_rows    = []

    print("\n" + "=" * 60)
    print("  Running Full Benchmark Suite")
    print("  (5 trials per measurement – averaged)")
    print("=" * 60)

    for n in DATASET_SIZES:
        print(f"\n  Dataset size = {n:,}")
        movies = loader.load_by_size(n)

        # --- A. Insertion ----------------------------------------------
        ins = benchmark_insertion(movies)
        ins["size"] = n
        insertion_rows.append(ins)
        print(f"    Insert  | Hash  : {ins['hash_ms']:>8.2f} ms   "
              f"Trie  : {ins['trie_ms']:>8.2f} ms")

        # --- B. Exact search -------------------------------------------
        ex = benchmark_exact_search(movies)
        ex["size"] = n
        exact_rows.append(ex)
        print(f"    Exact   | Hash  : {ex['hash_us']:>8.2f} µs   "
              f"Linear: {ex['linear_us']:>8.2f} µs")

        # --- C. Prefix search ------------------------------------------
        px = benchmark_prefix_search(movies)
        px["size"] = n
        prefix_rows.append(px)
        print(f"    Prefix  | Trie  : {px['trie_ms']:>8.4f} ms   "
              f"Linear: {px['linear_ms']:>8.4f} ms")

    return {
        "insertion": insertion_rows,
        "exact":     exact_rows,
        "prefix":    prefix_rows,
    }


# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_table(title: str, headers: list, rows: list) -> None:
    """Generic console table printer."""
    col_w = 14
    print(f"\n  {title}")
    line = "  " + "".join(f"{h:>{col_w}}" for h in headers)
    print(line)
    print("  " + "─" * (len(line) - 2))
    for r in rows:
        print("  " + "".join(f"{v:>{col_w}}" for v in r))
