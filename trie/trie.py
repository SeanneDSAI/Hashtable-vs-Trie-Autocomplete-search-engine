"""
trie/trie.py
------------
Prefix Tree (Trie) – built from scratch following the Week 10 lab.

Operations:
    - insert(movie)       : O(k)         add one movie
    - search(title)       : O(k)         exact match by clean_title
    - autocomplete(prefix): O(k + m)     all movies whose title starts with prefix

Where k = length of the query string, m = total characters in matched subtree.

Movies are inserted using their clean_title (lowercase, year stripped) as the
key, so all queries are case-insensitive.
"""

from trie.trie_node import TrieNode


class Trie:
    """
    Prefix Tree.

    The class owns the root TrieNode and provides public methods to
    insert movies, search for an exact title, and produce autocomplete
    suggestions for a given prefix.
    """

    def __init__(self):
        self.root = TrieNode()
        self._count = 0          # number of unique titles inserted

    # ------------------------------------------------------------------
    # Insert  – Week 10, Task 4
    # ------------------------------------------------------------------

    def insert(self, movie: dict) -> None:
        """
        Insert a movie record into the Trie, keyed on clean_title.

        Walks (or creates) one node per character.  Once the final
        character is reached, the node is marked is_end = True and the
        full movie dict is appended to that node's movies list.
        """
        word = movie["clean_title"]
        node = self.root
        for char in word:
            # setdefault returns an existing child or creates a new one
            node = node.children.setdefault(char, TrieNode())

        if not node.is_end:
            self._count += 1
        node.is_end = True
        node.movies.append(movie)

    # ------------------------------------------------------------------
    # Exact search
    # ------------------------------------------------------------------

    def search(self, title: str):
        """
        Exact-match lookup by clean_title (case-insensitive).

        Returns the first matching movie dict, or None if not found.
        """
        node = self._traverse(title.lower())
        if node and node.is_end and node.movies:
            return node.movies[0]
        return None

    # ------------------------------------------------------------------
    # Autocomplete (prefix search) – Week 10, Tasks 5 & 6
    # ------------------------------------------------------------------

    def autocomplete(self, prefix: str) -> list:
        """
        Return every movie whose clean_title begins with *prefix*.

        Steps:
            1. Walk to the node at the end of *prefix* (O(k)).
            2. DFS over its descendants, collecting movies stored at
               every is_end node (O(m)).

        Returns
        -------
        list of movie dicts (empty if prefix not present).
        """
        node = self._traverse(prefix.lower())
        if node is None:
            return []

        results: list = []
        self._dfs(node, results)
        return results

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Number of unique titles stored in the Trie."""
        return self._count

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _traverse(self, word: str):
        """
        Walk the Trie character-by-character following *word*.

        Returns the node at the end of the path or None if the path
        does not exist.
        """
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _dfs(self, node: TrieNode, results: list) -> None:
        """
        Depth-first search collecting all stored movies in the subtree
        rooted at *node*.
        """
        if node.is_end:
            results.extend(node.movies)
        for child in node.children.values():
            self._dfs(child, results)
