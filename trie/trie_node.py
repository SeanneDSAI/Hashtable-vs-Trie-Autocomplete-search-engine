"""
trie/trie_node.py
-----------------
Single node of a Trie (Prefix Tree).

Structure (matches Week 10 lab):
    - children   : dict mapping char -> TrieNode
    - is_end     : bool, True if this node completes a valid word
    - movies     : list of movie dicts that end at this node
                   (extension to the lab to support storing full records)
"""


class TrieNode:
    """
    Each TrieNode represents a single character position in the Trie.

    A path from the root to a node forms a string; if is_end is True,
    that string is a stored title and one or more movie records are
    attached to this node.
    """

    __slots__ = ("children", "is_end", "movies")

    def __init__(self):
        self.children: dict = {}     # char -> TrieNode
        self.is_end: bool = False
        self.movies: list = []       # movies whose clean_title ends here
