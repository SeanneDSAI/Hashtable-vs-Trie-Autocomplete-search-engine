"""
main.py
-------
Central system entry point for the DSAA2 assignment.

Responsibilities (per the assignment prompt):

  1. Load the MovieLens dataset
  2. Insert every movie into:
        - HashTable (exact search)
        - Trie       (prefix / autocomplete search)
  3. Run the full experimental framework:
        - Insertion timing
        - Exact search:  Hash vs Linear
        - Prefix search: Trie vs Linear
  4. Repeat each measurement 5 times across multiple dataset sizes
  5. Present results as console tables AND save Matplotlib charts to output/
  6. Demonstrate the system on the FULL dataset (87,585 movies) with
     real example queries, exporting prefix results to output/*.csv.

Run:
    python main.py
"""

import os
import csv
import time

import matplotlib
matplotlib.use("Agg")                 # non-interactive backend
import matplotlib.pyplot as plt

from data_loader.data_loader import MovieDataLoader
from hash_table import HashTable
from trie.trie import Trie
from benchmark import (
    run_full_benchmark,
    print_table,
    linear_search,
    linear_prefix_search,
    DATASET_SIZES,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

DATA_PATH  = os.path.join("data", "movies.csv")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------------

def banner(text: str, char: str = "=") -> None:
    print("\n" + char * 65)
    print(f"  {text}")
    print(char * 65)


def section(text: str) -> None:
    print(f"\n──  {text}  " + "─" * (60 - len(text)))


# ---------------------------------------------------------------------------
# Chart generation – called by code, not pre-built
# ---------------------------------------------------------------------------

COLORS = {
    "hash":   "#2196F3",
    "trie":   "#FF5722",
    "linear": "#4CAF50",
}


def save_insertion_chart(rows: list, path: str) -> None:
    sizes = [r["size"] for r in rows]
    hash_ms = [r["hash_ms"] for r in rows]
    trie_ms = [r["trie_ms"] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    width = 0.35
    x = range(len(sizes))
    ax.bar([i - width/2 for i in x], hash_ms, width, label="HashTable",
           color=COLORS["hash"])
    ax.bar([i + width/2 for i in x], trie_ms, width, label="Trie",
           color=COLORS["trie"])
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{s:,}" for s in sizes])
    ax.set_xlabel("Dataset Size (movies)")
    ax.set_ylabel("Avg Insertion Time (ms)")
    ax.set_title("Insertion Performance: HashTable vs Trie")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"    Chart saved → {path}")


def save_exact_search_chart(rows: list, path: str) -> None:
    sizes  = [r["size"] for r in rows]
    h_us   = [r["hash_us"]   for r in rows]
    l_us   = [r["linear_us"] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(sizes, h_us, marker="o", label="HashTable",     color=COLORS["hash"])
    ax.plot(sizes, l_us, marker="x", label="Linear search", color=COLORS["linear"],
            linestyle="--")
    ax.set_xlabel("Dataset Size (movies)")
    ax.set_ylabel("Avg Search Time per Query (µs)")
    ax.set_title("Exact Search Performance: HashTable vs Linear Search")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"    Chart saved → {path}")


def save_prefix_chart(rows: list, path: str) -> None:
    sizes   = [r["size"] for r in rows]
    t_ms    = [r["trie_ms"]   for r in rows]
    l_ms    = [r["linear_ms"] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(sizes, t_ms, marker="^", label="Trie",          color=COLORS["trie"])
    ax.plot(sizes, l_ms, marker="x", label="Linear search", color=COLORS["linear"],
            linestyle="--")
    ax.set_xlabel("Dataset Size (movies)")
    ax.set_ylabel("Avg Prefix Search Time (ms)")
    ax.set_title("Prefix Search Performance: Trie vs Linear Search")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"    Chart saved → {path}")


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------

def export_prefix_results(prefix: str, results: list, output_dir: str) -> str:
    """Write autocomplete results to output/prefix_search_<prefix>.csv."""
    safe = prefix.replace(" ", "_").lower()
    path = os.path.join(output_dir, f"prefix_search_{safe}.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "title", "genres"])
        for m in results:
            w.writerow([m["id"], m["title"], "|".join(m["genres"])])
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    banner("DSAA2 – HashTable vs Trie | MovieLens Search Benchmark")

    # ------------------------------------------------------------------ #
    # 1.  Load dataset                                                    #
    # ------------------------------------------------------------------ #
    section("1. Loading dataset")
    loader = MovieDataLoader(DATA_PATH)
    t0 = time.perf_counter()
    movies = loader.load_movies()
    load_ms = (time.perf_counter() - t0) * 1000
    print(f"    {len(movies):,} movies loaded in {load_ms:.1f} ms")
    print(f"    Sample record:")
    for k, v in movies[0].items():
        print(f"      {k:<12}: {v}")

    # ------------------------------------------------------------------ #
    # 2.  Build the two data structures on the full dataset               #
    # ------------------------------------------------------------------ #
    section("2. Building HashTable and Trie on full dataset")
    ht = HashTable()
    tr = Trie()

    t0 = time.perf_counter()
    for m in movies:
        ht.insert(m)
    ht_build = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for m in movies:
        tr.insert(m)
    tr_build = (time.perf_counter() - t0) * 1000

    print(f"    HashTable build : {ht_build:7.1f} ms   "
          f"({ht.entries:,} entries, {ht.collisions:,} collisions, "
          f"load factor {ht.load_factor():.3f})")
    print(f"    Trie build      : {tr_build:7.1f} ms   "
          f"({tr.size:,} unique titles)")

    # ------------------------------------------------------------------ #
    # 3.  Demo queries on the full dataset                                #
    # ------------------------------------------------------------------ #
    section("3. Demonstration queries (full dataset)")

    sample = movies[1234]
    sample_title = sample["clean_title"]

    # Exact search via HashTable
    t0 = time.perf_counter()
    h_hit = ht.search(sample_title)
    h_us = (time.perf_counter() - t0) * 1_000_000

    # Exact search via Linear scan
    t0 = time.perf_counter()
    l_hit = linear_search(movies, sample_title)
    l_us = (time.perf_counter() - t0) * 1_000_000

    print(f"    Exact-search query : '{sample_title}'")
    print(f"      HashTable  → {h_hit['title']:<40} ({h_us:8.2f} µs)")
    print(f"      Linear     → {l_hit['title']:<40} ({l_us:8.2f} µs)")
    if h_us > 0:
        print(f"      Speedup : {l_us / max(h_us, 0.01):.0f}× faster with HashTable")

    # Prefix search via Trie + linear comparison
    print(f"\n    Prefix queries (Trie autocomplete vs Linear scan):")
    for prefix in ["the", "star", "dark", "love", "bl"]:
        t0 = time.perf_counter()
        trie_hits = tr.autocomplete(prefix)
        trie_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        linear_hits = linear_prefix_search(movies, prefix)
        linear_ms = (time.perf_counter() - t0) * 1000

        print(f"      '{prefix:<5}' → Trie {len(trie_hits):>5} hits "
              f"in {trie_ms:6.3f} ms  |  "
              f"Linear {len(linear_hits):>5} hits in {linear_ms:6.3f} ms")

        # Export to CSV (limit 200 rows for readability)
        path = export_prefix_results(prefix, trie_hits[:200], OUTPUT_DIR)
        print(f"             exported → {path}")

    # ------------------------------------------------------------------ #
    # 4.  Full benchmark suite                                            #
    # ------------------------------------------------------------------ #
    section("4. Running benchmark suite across multiple dataset sizes")
    print(f"    Sizes: {DATASET_SIZES}")
    print(f"    Trials per measurement: 5")

    results = run_full_benchmark(DATA_PATH)

    # ------------------------------------------------------------------ #
    # 5.  Print result tables                                             #
    # ------------------------------------------------------------------ #
    banner("RESULTS  –  Tabular Summary", char="─")

    print_table(
        "Table 1.  Insertion time (ms) – averaged over 5 trials",
        ["Size", "HashTable (ms)", "Trie (ms)"],
        [
            [f"{r['size']:,}", f"{r['hash_ms']:.2f}", f"{r['trie_ms']:.2f}"]
            for r in results["insertion"]
        ],
    )

    print_table(
        "Table 2.  Exact search time (µs/query) – averaged over 5 trials",
        ["Size", "HashTable (µs)", "Linear (µs)", "Speedup"],
        [
            [
                f"{r['size']:,}",
                f"{r['hash_us']:.2f}",
                f"{r['linear_us']:.2f}",
                f"{r['linear_us'] / max(r['hash_us'], 0.001):.0f}×",
            ]
            for r in results["exact"]
        ],
    )

    print_table(
        "Table 3.  Prefix search time (ms/query) – averaged over 5 trials",
        ["Size", "Trie (ms)", "Linear (ms)", "Speedup"],
        [
            [
                f"{r['size']:,}",
                f"{r['trie_ms']:.4f}",
                f"{r['linear_ms']:.4f}",
                f"{r['linear_ms'] / max(r['trie_ms'], 0.0001):.1f}×",
            ]
            for r in results["prefix"]
        ],
    )

    # ------------------------------------------------------------------ #
    # 6.  Generate charts                                                 #
    # ------------------------------------------------------------------ #
    section("5. Generating Matplotlib charts")
    save_insertion_chart   (results["insertion"], os.path.join(OUTPUT_DIR, "chart_insertion.png"))
    save_exact_search_chart(results["exact"],     os.path.join(OUTPUT_DIR, "chart_exact_search.png"))
    save_prefix_chart      (results["prefix"],    os.path.join(OUTPUT_DIR, "chart_prefix_search.png"))

    banner("Run complete.  All output files saved to ./output/", char="─")


if __name__ == "__main__":
    main()
