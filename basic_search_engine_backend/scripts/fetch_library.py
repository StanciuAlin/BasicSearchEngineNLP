from search_engine.search.engine import SearchEngine
from search_engine.models.document import Document
import gutenbergpy.textget
import sys
import os


"""
Module: populate_db.py
Description: An automated ingestion pipeline designed to build a large-scale 
textual corpus. It handles document acquisition from Project Gutenberg, 
persistence in the SQLite document store, and the generation of a 
vector-based index using Scikit-Learn.
"""

# Add the project root to the system path to ensure proper resolution
# of the 'search_engine' package during execution.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def populate_library(count=1000):
    """
    Automates the acquisition of literary works and initializes system indexes.

    The workflow follows a rigorous ETL (Extract, Transform, Load) pattern:
    1. Checkpoint Verification: Resumes from the last known document ID to 
       avoid redundant network traffic.
    2. Data Acquisition: Fetches raw text from Project Gutenberg.
    3. Content Sanitization: Removes non-literary boilerplate headers/footers.
    4. Database Persistence: Commits the cleaned documents to SQLite.
    5. Index Construction: Triggers the Sklearn TF-IDF build process for the 
       newly added documents.

    Args:
        count (int): Target number of documents to maintain in the repository.
    """

    engine = SearchEngine()

    # CHECKPOINT: Determine current state of the document store
    existing_count = engine.doc_store.get_document_count()
    if existing_count >= count:
        print(
            f"Database already contains {existing_count} documents. No download required.")
        return
    elif existing_count > 0:
        print(
            f"Found {existing_count} documents. Resuming ingestion process...")
        start_index = existing_count + 1
    else:
        start_index = 1

    docs = []

    print(
        f"Initiating bulk download of {count} books from Project Gutenberg...")

    for i in range(start_index, count + 1):
        try:
            # Extraction: Retrieve raw binary text using the Gutenberg ID
            raw_book = gutenbergpy.textget.get_text_by_id(i)

            # Transformation: Strip standardized Project Gutenberg headers and footers
            # This ensures index quality by removing non-semantic boilerplate text.
            clean_book = gutenbergpy.textget.strip_headers(
                raw_book).decode('utf-8')

            # Modeling: Create a Document instance with necessary metadata
            doc = Document(
                doc_id=i,
                title=f"Gutenberg Book {i}",
                content=clean_book,
                path=f"gutenberg_{i}.txt"
            )
            docs.append(doc)

            if len(docs) % 10 == 0:
                print(f"Downloaded {len(docs)} books...")

        except Exception as e:
            # Many IDs in the Gutenberg sequence may be unavailable or non-textual
            continue

    if not docs:
        print("Failed to download documents. Please verify network connectivity.")
        return

    # Loading: Save the transformed documents into the persistent SQLite store
    print(f"Saving {len(docs)} documents to SQLite storage...")
    engine.doc_store.add_documents(docs)

    # Secondary Indexing: Generate the Sklearn-based vector space model
    # to serve as a benchmark or alternative retrieval method.
    print("Generating Scikit-Learn index for the updated corpus...")
    engine.sklearn_engine.build_index(docs)

    print("Success! Database and index have been successfully initialized in 'data/'.")


if __name__ == "__main__":
    # Execution entry point. The 'count' parameter can be adjusted based
    # on desired corpus size and available disk space.
    populate_library(count=100)
