import sqlite3
import os

"""
Module: inspect_db.py
Description: A diagnostic utility script used to verify the integrity and content 
of the SQLite document store. It provides a tabular overview of the indexed 
corpus directly from the database.
"""


def inspect_documents(db_path="data/library.db"):
    """
    Connects to the document database and prints a summary of all stored records.

    This function performs a low-level inspection of the 'documents' table, 
    extracting key metadata and a text fragment (snippet) to confirm that 
    the ingestion process was successful.

    Args:
        db_path (str): The file system path to the SQLite database file.

    Operational Logic:
        1. Connectivity Check: Verifies if the database file exists.
        2. SQL Execution: Uses the SUBSTR function to efficiently retrieve only 
           the beginning of the content, reducing memory overhead.
        3. Formatting: Cleans control characters (newlines) and truncates titles 
           to ensure a clean CLI tabular display.
    """

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at path: {db_path}")
        return

    try:
        # Establish a connection to the persistence layer
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query for ID, Title, Path, and the first 200 characters of the Content.
        # We leverage the SQLite SUBSTR function to extract the snippet server-side.
        query = "SELECT id, title, path, SUBSTR(content, 1, 200) FROM documents"
        cursor.execute(query)

        rows = cursor.fetchall()

        if not rows:
            print("The database is currently empty.")
            return

        # Table header for the diagnostic view
        print(f"{'ID':<6} | {'Title':<40} | {'Path':<30} | {'Content (Snippet)':<50}")
        print("-" * 130)

        for row in rows:
            doc_id, title, path, content_snippet = row

            # Clean NewLine characters for a consistent table alignment in the terminal
            clean_snippet = content_snippet.replace(
                '\n', ' ').replace('\r', ' ')

            # Truncate title if it exceeds the column width for visual clarity
            display_title = (title[:37] + '..') if len(title) > 37 else title

            print(
                f"{doc_id:<6} | {display_title:<40} | {path:<30} | {clean_snippet[:50]}...")

        print("-" * 130)
        print(f"Total documents indexed: {len(rows)}")

    except sqlite3.Error as e:
        print(f"SQLite operational error: {e}")
    finally:
        # Ensure the database connection is closed regardless of operation success
        if conn:
            conn.close()


if __name__ == "__main__":
    # Execution entry point for manual database inspection
    inspect_documents()
