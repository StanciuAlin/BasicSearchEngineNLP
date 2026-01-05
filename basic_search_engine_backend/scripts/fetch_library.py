from search_engine.search.engine import SearchEngine
from search_engine.models.document import Document
import gutenbergpy.textget
import sys
import os

# Adaugă rădăcina proiectului la calea de căutare pentru a permite importurile din search_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def populate_library(count=1000):
    """
    Descarcă cărți de pe Gutenberg și le salvează în baza de date SQLite.
    Apoi generează indexul profesional Sklearn.
    """
    engine = SearchEngine()

    # VERIFICARE: Dacă avem deja documente, oprim execuția
    existing_count = engine.doc_store.get_document_count()
    if existing_count >= count:
        print(
            f"Baza de date conține deja {existing_count} documente. Nu este necesară o nouă descărcare.")
        return
    elif existing_count > 0:
        print(
            f"S-au găsit deja {existing_count} documente. Se continuă descărcarea de unde s-a rămas...")
        start_index = existing_count + 1
    else:
        start_index = 1

    docs = []

    print(
        f"Se inițiază descărcarea a {count} cărți de pe Project Gutenberg...")

    for i in range(start_index, count + 1):
        try:
            # Descarcă textul brut folosind ID-ul cărții
            raw_book = gutenbergpy.textget.get_text_by_id(i)

            # Curăță textul de antetele și subsolurile Project Gutenberg
            clean_book = gutenbergpy.textget.strip_headers(
                raw_book).decode('utf-8')

            # Creăm obiectul Document (cu noul parametru 'path')
            doc = Document(
                doc_id=i,
                title=f"Gutenberg Book {i}",
                content=clean_book,
                path=f"gutenberg_{i}.txt"
            )
            docs.append(doc)

            if len(docs) % 10 == 0:
                print(f"Am descărcat {len(docs)} cărți...")

        except Exception as e:
            # Multe ID-uri pot să nu fie disponibile sau să nu fie în format text
            continue

    if not docs:
        print("Nu s-au putut descărca documente. Verificați conexiunea la internet.")
        return

    print(f"Se salvează {len(docs)} documente în SQLite...")
    engine.doc_store.add_documents(docs)

    print("Se generează indexul profesional (Sklearn) pentru noile documente...")
    engine.sklearn_engine.build_index(docs)

    print("Succes! Baza de date și indexul au fost create în folderul 'data/'.")


if __name__ == "__main__":
    # Poți modifica numărul de cărți aici (ex: count=100 pentru un test rapid)
    # aici am redus la 10 pentru testare rapidă, dar trebuie 1000+
    populate_library(count=300)
