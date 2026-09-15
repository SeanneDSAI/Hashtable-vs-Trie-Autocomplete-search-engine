# Movie Search Benchmark: Hash Table vs Trie

A Python project that indexes a catalogue of 87,585 movie titles into two data structures built from scratch, a hash table and a trie, then measures how much faster each one is than a plain linear scan.

The hash table answers exact title lookups. The trie answers prefix lookups, the kind that power an autocomplete box. Both are benchmarked against a sequential search over the same data so the difference between constant time, prefix-length time and linear time is visible in real numbers rather than just big-O notation.

## What it does

- Loads a MovieLens-format CSV and normalises each title (strips the trailing release year, lowercases it) so lookups are case-insensitive
- Builds a hash table keyed on the cleaned title, using a hand-written djb2 hash and separate chaining for collisions
- Builds a trie where every node is one character and full movie records hang off the nodes that end a title
- Runs three timed experiments across five dataset sizes, averaging five trials each
- Prints result tables to the console, saves matplotlib charts to `output/`, and exports autocomplete results to CSV

No library data structures are used for the indexes. The hash function, collision handling, trie nodes and depth-first traversal are all written by hand.

## Project structure

```
CA 2 Final/
├── main.py                 Entry point: builds both indexes, runs demos and benchmarks
├── benchmark.py            The three experiments plus linear-search baselines
├── hash_table.py           Hash table with djb2 hashing and separate chaining
├── trie/
│   ├── trie.py             Trie: insert, exact search, autocomplete
│   └── trie_node.py        Single trie node (children, is_end, movies)
├── data_loader/
│   └── data_loader.py      CSV reader and title cleaner
├── data/
│   └── movies.csv          Dataset
└── output/                 Generated charts and CSV exports
```

## How the two structures work

### Hash table

A fixed array of 131,071 buckets, a large prime chosen to keep the load factor low and spread keys evenly. The hash function is djb2, implemented directly rather than calling Python's `hash()`:

```
h = 5381
for each character c:  h = (h * 33) XOR ord(c)
```

The result is masked to 32 bits and reduced modulo the table size. Collisions are handled by separate chaining, where each bucket is a list of `(key, movie)` tuples. Inserting a title that already exists updates it in place instead of duplicating it. The table tracks its entry count, collision count and load factor, so the structural health of the index can be reported alongside the timings.

Lookup is O(1) on average and O(n) in the worst case where every key lands in one bucket.

### Trie

Each node holds a dictionary of child characters, a flag marking whether a valid title ends there, and the list of movie records for that title. Inserting a title walks one node per character, creating nodes as needed. Because several movies can share a cleaned title, a node holds a list rather than a single record.

Autocomplete has two stages. First it walks to the node at the end of the prefix, which costs O(k) where k is the prefix length. Then it runs a depth-first search over everything below that node, collecting every stored movie, which costs O(m) where m is the size of the matched subtree. The total is O(k + m) and, crucially, does not depend on the size of the full dataset.

## The experiments

All timing uses `time.perf_counter()`, the highest-resolution monotonic clock available. Every measurement is repeated five times and the mean is reported, which smooths out interference from other processes. Dataset sizes are 1,000, 5,000, 10,000, 50,000 and 87,585 (the full file).

**A. Insertion.** How long it takes to build each structure from scratch. Hash table against trie.

**B. Exact search.** Ten query titles are picked at even intervals through the dataset and looked up in both the hash table and a linear scan. Results are reported in microseconds per query, with the speedup ratio.

**C. Prefix search.** Five prefixes (`the`, `star`, `dark`, `love`, `bl`) are resolved by trie autocomplete and by a linear scan with `startswith`. Results are reported in milliseconds per query, with the speedup ratio.

The expected pattern is that hash and trie lookup times stay roughly flat as the dataset grows while the linear scan climbs in proportion to it, so the gap widens with every step up in size.

## Running it

Python 3.8 or later. One dependency:

```bash
pip install matplotlib
```

Run from inside the project folder so the relative paths to `data/` and `output/` resolve:

```bash
python main.py
```

A full run takes a few minutes, most of it in the linear-search baselines at the larger dataset sizes.

## What it prints and saves

The console output moves through six stages: loading the dataset, building both structures on the full set (with entry counts, collision counts and load factor), running live demonstration queries, running the benchmark suite, printing three result tables, and generating the charts.

Files written to `output/`:

| File | Contents |
|---|---|
| `chart_insertion.png` | Bar chart, build time for both structures at each dataset size |
| `chart_exact_search.png` | Line chart, hash table against linear scan |
| `chart_prefix_search.png` | Line chart, trie against linear scan |
| `prefix_search_<prefix>.csv` | Autocomplete results for each demo prefix, capped at 200 rows |

The charts are generated by the code at run time using matplotlib's non-interactive backend, so nothing needs to be drawn by hand and the run works headless.

## Dataset

`data/movies.csv` in MovieLens format, with the columns `movieId`, `title` and `genres`. Titles carry the release year in brackets and genres are pipe-separated. The loader strips the year, lowercases the title for indexing, keeps the original title for display, and splits genres into a list.

To use a different catalogue, keep those three columns in that order and point `DATA_PATH` in `main.py` at the new file.
