import sqlite3

db_path = "data/library.db"  # Standard path to the database in the project

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

sql_command = """
INSERT INTO documents (id, title, path, content) VALUES 
(100001, 'Small doc 1', 'small_doc1.txt', 'Natural language processing is a branch of artificial intelligence.
This document introduces basic search engines and inverted indexes.'),
(100002, 'Small doc 2', 'small_doc2.txt', 'A search engine indexes documents and ranks them using tf idf and cosine similarity.
Term frequency and inverse document frequency are core concepts in information retrieval.
'),
(100003, 'Small doc 3', 'small_doc3.txt', 'Python is often used to build prototypes for information retrieval systems.
FastAPI can expose a search API that is consumed by a web frontend.
');
"""

try:
    cursor.execute(sql_command)
    conn.commit()
    print("The documents were inserted successfully into the database.")
except sqlite3.IntegrityError:
    print("Error: Some IDs already exist in the database. Insertion skipped.")
finally:
    conn.close()
