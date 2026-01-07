import sqlite3
import json

"""
Module: cache_manager.py
Description: Implements a persistent caching layer using SQLite to store and 
retrieve search results, optimizing system performance by reducing redundant 
computational overhead for frequent queries.
"""


class SearchCache:
    """
    A manager for handling search result persistence.

    This class interfaces with a SQLite database to store the results of expensive 
    ranking operations (BM25, TF-IDF). It employs a Least Recently Used (LRU) 
    inspired cleanup mechanism by limiting the total number of cached entries.
    """

    def __init__(self, db_path="data/library.db"):
        """
        Initializes the cache manager and ensures the storage table exists.

        Args:
            db_path (str): The file path to the SQLite database used for storage.
        """

        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """
        Creates the 'search_cache' table if it does not already exist.

        The table schema includes a unique cache_key (hash of query + params), 
        the results stored as a JSON string, and a timestamp for maintenance.
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE,
                    results_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def get(self, key):
        """
        Retrieves cached search results based on a unique key.

        Args:
            key (str): The unique identifier for a specific query and configuration.

        Returns:
            dict: The deserialized search results if a match is found; otherwise, None.
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT results_json FROM search_cache WHERE cache_key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def set(self, key, results):
        """
        Persists search results in the database and performs cache maintenance.

        This method inserts or replaces the result for a given key. To prevent 
        unbounded database growth, it maintains a strict limit of the 50 most 
        recent entries, deleting older records automatically.

        Args:
            key (str): The unique identifier generated for the search parameters.
            results (dict): The result set to be serialized and stored.

        Complexity:
            O(1) for insertion, followed by a cleanup operation to maintain the size limit.
        """

        with sqlite3.connect(self.db_path) as conn:
            # Insert the new result or update if the key exists
            try:
                conn.execute("INSERT OR REPLACE INTO search_cache (cache_key, results_json) VALUES (?, ?)",
                             (key, json.dumps(results)))

                # Maintain a 50-entry limit: Delete the oldest entries exceeding the threshold
                conn.execute("""
                    DELETE FROM search_cache 
                    WHERE id NOT IN (
                        SELECT id FROM search_cache 
                        ORDER BY id DESC LIMIT 50
                    )
                """)
                conn.commit()
            except Exception as e:
                # Log cache errors to console for diagnostic purposes
                print(f"Cache error: {e}")
