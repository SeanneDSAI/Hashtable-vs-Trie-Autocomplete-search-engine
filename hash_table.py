"""
hash_table.py
-------------
Custom Hash Table (Hash Map) – built from scratch following the Week 11 lab.

Design (matches the lab structure):
    - Fixed-size array of buckets, initialised at construction
    - Each bucket is a Python list (separate chaining for collisions)
    - Default size 131,071 (large prime → reduces clustering)
    - Hash function uses Python's built-in hash() reduced modulo the
      table size, plus an alternative djb2 implementation for strings

Operations:
    insert(movie)   : O(1) average,  O(n) worst-case (everything collides)
    search(title)   : O(1) average,  O(n) worst-case
"""


class HashTable:
    """
    Hash Map keyed on movie 'clean_title' (lowercase, year-stripped).

    Each bucket holds a list of (key, movie_dict) tuples so that
    duplicate-title collisions are preserved instead of overwritten.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, size: int = 131_071):
        """
        Parameters
        ----------
        size : int
            Number of buckets in the underlying table.  A large prime
            number keeps the load factor low and helps spread keys.
        """
        self.size = size
        self.table = [[] for _ in range(size)]   # separate chaining
        self.collisions = 0                      # diagnostic counter
        self.entries = 0                         # number of stored movies

    # ------------------------------------------------------------------
    # Hash function – djb2 (string hash from scratch)
    # ------------------------------------------------------------------

    def hash(self, key: str) -> int:
        """
        djb2 hash function:
            h = 5381
            for each character c:  h = (h * 33) XOR ord(c)

        Demonstrates the internal mechanics rather than relying on
        Python's built-in hash().
        """
        h = 5381
        for char in key:
            h = ((h << 5) + h) ^ ord(char)        # h * 33 XOR ord(c)
            h &= 0xFFFFFFFF                       # restrict to 32 bits
        return h % self.size

    # ------------------------------------------------------------------
    # Insert  – Week 11, Task 6
    # ------------------------------------------------------------------

    def insert(self, movie: dict) -> None:
        """
        Insert a movie into the table, keyed on its clean_title.

        On collision the new entry is appended to the bucket list and
        the collision counter is incremented.
        """
        key = movie["clean_title"]
        index = self.hash(key)
        bucket = self.table[index]

        if len(bucket) > 0:
            self.collisions += 1
            # Update if the title already exists in this bucket
            for i, (k, _) in enumerate(bucket):
                if k == key:
                    bucket[i] = (key, movie)
                    return

        bucket.append((key, movie))
        self.entries += 1

    # ------------------------------------------------------------------
    # Search  – Week 11, Task 7
    # ------------------------------------------------------------------

    def search(self, title: str):
        """
        Exact-match lookup by clean_title (case-insensitive).

        Returns the matching movie dict or None.
        """
        key = title.lower()
        index = self.hash(key)
        for k, movie in self.table[index]:
            if k == key:
                return movie
        return None

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def load_factor(self) -> float:
        """Ratio of stored entries to bucket count."""
        return self.entries / self.size

    def __len__(self) -> int:
        return self.entries
