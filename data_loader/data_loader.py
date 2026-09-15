"""
data_loader/data_loader.py
--------------------------
MovieDataLoader: reads movies.csv and produces a list of dictionaries.

Each movie is stored as:
    {
        "id":           int,
        "title":        str,   # original title incl. year
        "clean_title":  str,   # year removed, lowercased (used for hashing & trie)
        "genres":       list   # list of genre strings
    }

This matches the schema specified in the assignment prompt.
"""

import re
import csv


class MovieDataLoader:
    """
    Reads a MovieLens-format CSV file and converts it into a list of
    movie dictionaries.

    Supports:
      - Full load (all rows)
      - load_by_size(n) → first n rows, used for benchmarking subsets
    """

    # Regex used to strip trailing release year from a title
    _YEAR_RE = re.compile(r"\s*\(\d{4}\)\s*$")

    def __init__(self, filepath: str, delimiter: str = ","):
        """
        Parameters
        ----------
        filepath  : path to the CSV file
        delimiter : column separator (default ',')
        """
        self.filepath = filepath
        self.delimiter = delimiter
        self.movies: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_movies(self, max_records: int = None) -> list:
        """
        Read the CSV and return a list of movie dictionaries.

        Parameters
        ----------
        max_records : int or None
            If given, stop after this many valid rows.

        Returns
        -------
        list of dict (see schema above)
        """
        movies = []
        with open(self.filepath, encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh, delimiter=self.delimiter)
            next(reader)  # skip header

            for row in reader:
                if len(row) < 3:
                    continue                         # skip malformed rows

                movie = self._parse_row(row)
                if movie is None:
                    continue

                movies.append(movie)
                if max_records is not None and len(movies) >= max_records:
                    break

        self.movies = movies
        return movies

    def load_by_size(self, n: int) -> list:
        """Convenience: return only the first *n* movie records."""
        return self.load_movies(max_records=n)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_row(self, row: list):
        """Convert a raw CSV row into the movie dictionary schema."""
        try:
            movie_id = int(row[0])
        except ValueError:
            return None

        original_title = row[1].strip()
        clean = self._clean_title(original_title)
        genres = [g.strip() for g in row[2].strip().split("|") if g.strip()]

        return {
            "id":           movie_id,
            "title":        original_title,
            "clean_title":  clean,
            "genres":       genres,
        }

    def _clean_title(self, title: str) -> str:
        """Remove the trailing year and lowercase the title."""
        no_year = self._YEAR_RE.sub("", title).strip()
        return no_year.lower()
