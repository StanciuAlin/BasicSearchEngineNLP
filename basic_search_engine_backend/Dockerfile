# Folosim o imagine oficială de Python
FROM python:3.11-slim

WORKDIR /app

# Instalăm dependențele sistem
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiem doar requirements.txt prima dată (pentru a folosi cache-ul Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descarcă modelul spaCy pentru limba engleză
RUN python -m spacy download en_core_web_sm

# Dacă ai nevoie și de română:
# RUN python -m spacy download ro_core_news_sm

# ACUM copiem restul codului (inclusiv folderul 'scripts')
COPY . .

# Executăm scripturile de configurare după ce fișierele sunt prezente în container
RUN python scripts/setup_nltk.py
RUN python -m scripts.fetch_library

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]