import gutenbergpy.textget
import os

"""
Module: gutenberg_downloader.py
Description: A data acquisition utility that interfaces with the Project Gutenberg 
API. This script automates the collection of large-scale literary corpora for 
testing the search engine's scalability and retrieval accuracy.
"""


def download_gutenberg_book(book_id, dest_folder="data/docs"):
    """
    Downloads, cleans, and persists a book from Project Gutenberg by its unique ID.

    This process is a critical part of the ETL (Extract, Transform, Load) pipeline:
    1. Extraction: Retrieves the raw binary text from the Gutenberg servers.
    2. Transformation: Strips the standardized Project Gutenberg headers and 
       footers (metadata) to ensure only the literary content is indexed.
    3. Loading: Saves the processed text as a .txt file in the target directory.

    Args:
        book_id (int): The unique numerical identifier assigned by Project Gutenberg.
        dest_folder (str): The local directory where the document will be stored.

    Complexity:
        O(B), where B is the size of the book in bytes, as the entire content 
        must be processed for header stripping and written to disk.
    """

    # Ensure the destination directory exists to prevent I/O errors
    os.makedirs(dest_folder, exist_ok=True)

    # Step 1: Download the raw byte-stream of the book
    raw_book = gutenbergpy.textget.get_text_by_id(book_id)

    # Step 2: Clean the text by removing non-literary boilerplate information
    # This ensures the inverted index is not polluted with generic legal notices.
    clean_book = gutenbergpy.textget.strip_headers(raw_book)

    # Step 3: Persist the book as a .txt file for the Search Engine to index
    file_path = os.path.join(dest_folder, f"gutenberg_{book_id}.txt")
    with open(file_path, "wb") as f:
        f.write(clean_book)

    print(f"Book {book_id} successfully saved to {file_path}")


# Example Usage: Download iconic literary works for benchmarking
# 2701: Moby Dick by Herman Melville
# 1513: Romeo and Juliet by William Shakespeare
download_gutenberg_book(2701)
download_gutenberg_book(1513)
