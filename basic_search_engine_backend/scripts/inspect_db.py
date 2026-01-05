import sqlite3
import os


def inspect_documents(db_path="data/library.db"):
    if not os.path.exists(db_path):
        print(f"Eroare: Baza de date nu a fost găsită la calea: {db_path}")
        return

    try:
        # Ne conectăm la baza de date
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Executăm interogarea pentru ID, Titlu, Path și primele 200 de caractere din Content
        # Folosim funcția SUBSTR din SQLite pentru a extrage doar începutul textului direct din baza de date
        query = "SELECT id, title, path, SUBSTR(content, 1, 200) FROM documents"
        cursor.execute(query)

        rows = cursor.fetchall()

        if not rows:
            print("Baza de date este goală.")
            return

        print(f"{'ID':<6} | {'Titlu':<40} | {'Path':<30} | {'Content (Snippet)':<50}")
        print("-" * 130)

        for row in rows:
            doc_id, title, path, content_snippet = row

            # Curățăm caracterele de tip NewLine pentru o afișare mai frumoasă în tabel
            clean_snippet = content_snippet.replace(
                '\n', ' ').replace('\r', ' ')

            # Trunchiem titlul dacă este prea lung pentru tabel
            display_title = (title[:37] + '..') if len(title) > 37 else title

            print(
                f"{doc_id:<6} | {display_title:<40} | {path:<30} | {clean_snippet[:50]}...")

        print("-" * 130)
        print(f"Total documente găsite: {len(rows)}")

    except sqlite3.Error as e:
        print(f"Eroare SQLite: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    inspect_documents()
