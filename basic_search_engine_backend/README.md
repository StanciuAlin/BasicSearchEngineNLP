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

De adaugat: pip install gutenbergpy

Trebuie să creez baza de date înainte?

Nu, nu trebuie să creezi manual fișierul sau tabelele. Totuși, trebuie să parcurgi un pas inițial pentru a o popula cu date:

Baza de date va fi goală inițial. Trebuie să rulezi scriptul fetch_library.py (sau populate_library) o singură dată.

Acest script va descărca textele de pe Gutenberg, va crea obiectele Document și le va salva în baza de date folosind metoda add_documents.

Datele sunt stocate fizic într-un singur fișier situat în calea: basic_search_engine_backend/data/library.db.

Pentru a vizualiza conținutul bazei de date (tabelele și rândurile cu cărți), ai mai multe opțiuni:

DB Browser for SQLite: Este cea mai populară unealtă gratuită cu interfață vizuală. Descarci aplicația, deschizi fișierul library.db și poți naviga prin tabelul documents ca într-un tabel Excel.

Extensie VS Code: Poți instala extensia "SQLite Viewer" direct în Visual Studio Code. După instalare, dai click dreapta pe fișierul .db și alegi "Open With -> SQLite Viewer".

Linia de comandă: Dacă ai sqlite3 instalat, poți rula în terminal:

Bash
sqlite3 data/library.db
SELECT id, title FROM documents LIMIT 10;
Rezumatul fluxului:

Codul creează fișierul library.db și structura tabelului la prima rulare.

Scriptul de fetch umple tabelul cu cele 1000 de cărți.

Baza de date rămâne pe disc, astfel încât la următoarele porniri ale aplicației, motorul de căutare doar citește din ea, fără a mai descărca nimic.

Rularea ca modul (Recomandat)

Cea mai sigură metodă este să rulezi scriptul direct din rădăcina folderului basic_search_engine_backend folosind parametrul -m. Această abordare permite Python să rezolve automat ierarhia de pachete.

Deschide terminalul și navighează în folderul principal al backend-ului: cd path/to/basic_search_engine_backend

Rulează scriptul astfel: python3 -m scripts.fetch_library
