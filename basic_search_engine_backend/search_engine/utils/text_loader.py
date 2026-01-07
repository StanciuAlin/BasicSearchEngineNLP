import os
from typing import List
from ..models.document import Document


"""
Module: text_loader.py
Description: Provides utility functions for ingesting raw text data from the local 
file system into the internal Document model structure.
"""


def load_documents_from_folder(folder: str) -> List[Document]:
    """
    Loads text documents from a specified directory and initializes Document objects.

    This function iterates through a folder, filters for files with a .txt extension, 
    and reads their content. Each file is assigned a unique incremental ID and the 
    filename (without extension) is used as the document title.

    Args:
        folder (str): The relative or absolute path to the directory containing 
                      the .txt files to be indexed.

    Returns:
        List[Document]: A list of Document model instances containing the ID, 
                        title, and full text content for each file found.

    Complexity:
        O(N * M), where N is the number of files and M is the average size of 
        each file, as every file must be opened and read into memory.
    """

    docs: List[Document] = []
    doc_id = 0
    # Sorting ensures consistent ID assignment across different executions
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(folder, fname)
        # Reading content with UTF-8 encoding to support diverse literary texts
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Use filename as title for the search result snippets
        title = os.path.splitext(fname)[0]
        docs.append(Document(doc_id=doc_id, title=title, content=content))
        doc_id += 1
    return docs
