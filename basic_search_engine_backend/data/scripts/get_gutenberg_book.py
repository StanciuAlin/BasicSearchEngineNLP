import gutenbergpy.textget
import os


def download_gutenberg_book(book_id, dest_folder="data/docs"):
    # Creează folderul dacă nu există
    os.makedirs(dest_folder, exist_ok=True)

    # Descarcă textul brut
    raw_book = gutenbergpy.textget.get_text_by_id(book_id)

    # Curăță textul de headerele Project Gutenberg
    clean_book = gutenbergpy.textget.strip_headers(raw_book)

    # Salvează ca fișier .txt
    file_path = os.path.join(dest_folder, f"gutenberg_{book_id}.txt")
    with open(file_path, "wb") as f:
        f.write(clean_book)

    print(f"Cartea {book_id} a fost salvată în {file_path}")


# Exemplu: Descarcă Moby Dick (2701) și Romeo and Juliet (1513)
download_gutenberg_book(2701)
download_gutenberg_book(1513)
