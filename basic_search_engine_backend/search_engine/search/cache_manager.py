import sqlite3
import json


class SearchCache:
    def __init__(self, db_path="data/library.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT results_json FROM search_cache WHERE cache_key = ?", (key,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    def set(self, key, results):
        with sqlite3.connect(self.db_path) as conn:
            # Inserăm rezultatul nou
            try:
                conn.execute("INSERT OR REPLACE INTO search_cache (cache_key, results_json) VALUES (?, ?)",
                             (key, json.dumps(results)))

                # Menținem limita de 50: Ștergem cele mai vechi intrări care depășesc limita
                conn.execute("""
                    DELETE FROM search_cache 
                    WHERE id NOT IN (
                        SELECT id FROM search_cache 
                        ORDER BY id DESC LIMIT 50
                    )
                """)
                conn.commit()
            except Exception as e:
                print(f"Cache error: {e}")
