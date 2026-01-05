# Basic Search Engine Backend (Python / FastAPI)

Simple classic IR backend used by a Blazor UI.

## Run

```bash
cd backend_python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

---

# Comenzi

De adaugat: pip install gutenbergpy

python3 -m scripts.fetch_library

---

---

# SQLite

Trebuie să creez baza de date înainte?

    Nu, nu trebuie să creezi manual fișierul sau tabelele. Totuși, trebuie să parcurgi un pas inițial pentru a o popula cu date:

Comanda: python3 -m scripts.fetch_library

Baza de date va fi goală inițial. Trebuie să rulezi scriptul fetch_library.py (sau populate_library) o singură dată.
Scriptul fetch_library.py va descărca textele de pe Gutenberg, va crea obiectele Document și le va salva în baza de date folosind metoda add_documents.
Datele sunt stocate fizic într-un singur fișier situat în calea: basic_search_engine_backend/data/library.db.

Pentru a vizualiza conținutul bazei de date (tabelele și rândurile cu cărți), ai mai multe opțiuni:

1. DB Browser for SQLite: Este cea mai populară unealtă gratuită cu interfață vizuală. Descarci aplicația, deschizi fișierul library.db și poți naviga prin tabelul documents ca într-un tabel Excel.
2. Extensie VS Code: Poți instala extensia "SQLite Viewer" direct în Visual Studio Code. După instalare, dai click dreapta pe fișierul .db și alegi "Open With -> SQLite Viewer".
3. Linia de comandă: Dacă ai sqlite3 instalat, poți rula în terminal:
   Bash
   sqlite3 data/library.db
   SELECT id, title FROM documents LIMIT 10;

Rezumatul fluxului:

1. Codul creează fișierul library.db și structura tabelului la prima rulare.
2. Scriptul de fetch umple tabelul cu cele 1000 de cărți.
   Baza de date rămâne pe disc, astfel încât la următoarele porniri ale aplicației, motorul de căutare doar citește din ea, fără a mai descărca nimic.

Rularea ca modul (Recomandat)

Cea mai sigură metodă este să rulezi scriptul direct din rădăcina folderului basic_search_engine_backend folosind parametrul -m. Această abordare permite Python să rezolve automat ierarhia de pachete. 1. Deschide terminalul și navighează în folderul principal al backend-ului: cd path/to/basic_search_engine_backend 2. Rulează scriptul astfel: python3 -m scripts.fetch_library (l-am adaugat in requirements.txt)

---

---

# Paginare

Note despre implementare:

1. Eficiență: Căutarea se realizează pe toate documentele din baza de date SQLite, dar în memorie sunt procesate doar ID-urile și scorurile. Textele complete sunt încărcate din baza de date doar pentru cele 10 rezultate care trebuie afișate pe pagina curentă.
2. Navigare: Butoanele de paginare apelează funcția PerformSearch cu noul index al paginii, actualizând interfața fără a reîncărca întreaga pagină.

---

---

# Docker Compose

Comenzi:

## Oprește și șterge containerele/rețelele vechi

docker-compose down

## Șterge cache-ul de build pentru a fi sigur că ia noul port

docker builder prune -f

## Pornește din nou

docker-compose up --build

## Pentru benchmark:

Varianta A (Recomandată - folosește numele serviciului):

docker-compose exec backend python3 -m scripts.run_benchmark

Varianta B (Dacă folosești numele containerului găsit la pasul 3):

docker exec -it NUME_CONTAINER_AICI python3 -m scripts.run_benchmark

## Inspect DB

docker-compose exec backend python3 inspect_db.py

Ce face acest script:

SUBSTR(content, 1, 200): Aceasta este o funcție SQLite care extrage fragmentul de text direct la nivelul bazei de date, fiind mult mai rapidă decât încărcarea întregului text în memoria Python.

Formatare tabelară: Aliniază coloanele pentru a putea identifica ușor ID-ul asociat fiecărei cărți (necesar pentru fișierul tău eval_queries.json).

Curățare text: Elimină trecerile la rând nou din snippet-ul de conținut pentru a păstra fiecare document pe o singură linie în terminal.

---

## Metrici:

MRR

MAP

nDCG@5

Precision@5 (P@5). Această metrică îți va spune, în medie, câte dintre primele 5 rezultate returnate de motorul tău sunt cu adevărat relevante. Dacă P@5 este 0.8, înseamnă că 4 din cele 5 rezultate de pe prima pagină sunt corecte.
