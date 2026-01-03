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
