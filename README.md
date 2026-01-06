# Basic Search Engine NLP

> A complete, classic **Information Retrieval (IR)** system consisting of a high-performance **Python Backend (FastAPI)** and a modern **.NET Blazor Frontend**.  
> The system supports indexing large text corpora and searching them using multiple ranking algorithms.


## 🏗️ Architecture & Technologies

The project is split into two main services that communicate via a **REST API**.


### 🐍 Backend (Python 3.13 + FastAPI)

- **Core Logic:** Custom implementation of an **Inverted Index**
- **Ranking Algorithms:**
  - TF-IDF (Cosine Similarity)
  - BM25 (with adjustable `k1` and `b` parameters)
  - Jaccard Similarity
  - Integration with **Scikit-Learn**
- **Storage:**
  - SQLite for document persistence
  - Disk-based cache system for faster result retrieval
- **Preprocessing Pipeline (Modular):**
  - Tokenization
  - Stop-word removal
  - Stemming

### 🖥️ Frontend (Blazor Server-Side)

- Intuitive user interface for performing searches
- Features:
  - Pagination
  - Real-time algorithm comparison
  - Result snippet visualization
- Uses **Bootstrap Icons** for a richer visual experience

### 🐳 Infrastructure

- **Docker & Docker Compose**
  - Orchestrates both services
  - Ensures a consistent and reproducible environment

## 📂 Project Structure

The project is organized into two main directories, separating the logic of the search engine from the presentation layer:

```plaintext
├── basic_search_engine_backend/       # Python FastAPI Backend
│   ├── data/                          # SQLite database and evaluation datasets
│   ├── scripts/                       # Maintenance, population, and benchmark scripts
│   ├── search_engine/                 # Core Search Engine logic
│   │   ├── evaluation/                # IR metrics calculation (MRR, NDCG, P@5)
│   │   ├── indexing/                  # Inverted Index, BM25, and TF-IDF implementations
│   │   ├── models/                    # Data models for Documents and Search Results
│   │   ├── preprocessing/             # NLP strategies and text cleaning pipeline
│   │   └── search/                    # Search orchestration and Cache Management
│   └── app.py                         # API endpoints and FastAPI configuration
│
├── BasicSearchEngine.Web.Blazor/      # .NET Blazor Frontend
│   ├── Pages/                         # Razor components (Search UI, Document views)
│   ├── Shared/                        # Common UI layouts
│   └── Program.cs                     # Frontend service configuration
│
└── docker-compose.yml                 # Service orchestration
```

## How to Run

### ✅ Recommended: Docker Compose

The easiest way to start the entire ecosystem is using Docker:

```bash
# Clone the repository and navigate to the root folder
docker-compose up --build
```

- **Frontend:** http://localhost:5001  
- **Backend API:** http://localhost:8000  


### 🛠️ Manual Local Run

#### Backend

```bash
cd basic_search_engine_backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

#### Frontend

- Ensure the `BaseAddress` in `Program.cs` is pointed to your backend (e.g. `http://localhost:8000/`)
- Run the project using **Visual Studio** or:

```bash
dotnet run
```

## SQLite Database

### 📚 Populating Data

To download and index books from the **Project Gutenberg** library, use the provided script:

```bash
docker-compose exec backend python3 -m scripts.fetch_library
```

### 🗄️ Data Inspection

You can inspect the SQLite database directly from the terminal:

```bash
docker-compose exec backend python3 inspect_db.py
```

## Benchmarking
### 🧪 Running Benchmark Tests

Evaluate the performance of various algorithms (**MRR**, **nDCG@5**, **P@5**) using the benchmark script:

```bash
# Run benchmark on the normal dataset
docker-compose exec backend python3 -m scripts.run_benchmark
```
```bash
# Run benchmark on the large dataset
docker-compose exec backend python3 -m scripts.run_benchmark --size large
```

### 📊 Results

When you run the benchmark script, you will see an evaluation table comparing the different ranking methods implemented in the system:

```plaintext
--- Load queries from data/eval_queries.json ---
Indexing 1000 documents from the database...
Indexing complete with success!

Method               | MRR      | nDCG@5   | P@5     
-------------------------------------------------------
TF-IDF               | 0.824    | 0.756    | 0.680   
BM25 (Standard)      | 0.892    | 0.812    | 0.740   
BM25 (Tuned)         | 0.915    | 0.845    | 0.785   
Jaccard              | 0.450    | 0.380    | 0.310
```

### 🔍 What these metrics mean

- **MRR (Mean Reciprocal Rank):** Indicates how quickly the first relevant document appears (closer to 1.0 is better).  
- **nDCG@5:** Measures the quality of the ranking order based on the position of relevant results.  
- **P@5 (Precision at 5):** The percentage of relevant documents found within the first 5 results.


## Relevant Technical Details
### 🌐 API Endpoints

- `GET /search/tfidf`  
  → Search based on **Cosine Similarity**

- `GET /search/bm25`  
  → Search using the **BM25 probabilistic algorithm**

- `GET /search/compare`  
  → Returns scores for **all algorithms simultaneously** for comparison



### 🧠 Advanced Features

#### 🏗️ Modular NLP Factory

The system implements a **Factory Pattern** for its preprocessing pipeline. This allows seamless switching between different NLP strategies, such as:

- Custom (rule-based)
- NLTK
- Scikit-Learn

This design ensures maximum flexibility in how text is tokenized, normalized, and processed.


#### 🔗 Boolean & Hybrid Search Logic

Beyond simple ranking, the engine supports:

- **AND** operator
- **OR** operator
- **HYBRID** operator

In **Hybrid** mode, the system applies a relevance boost (e.g., **50%**) to documents that contain **all query terms**, effectively prioritizing precision without sacrificing recall.


#### 🧠 Intelligent Search Caching

To minimize computational overhead, a **persistent Search Cache** is implemented using **SQLite**.

- Stores search results indexed by a unique key composed of:
  - Query string
  - Algorithm choice
  - Algorithm parameters (e.g., `k1`, `b`)

This dramatically improves response time for repeated or similar queries.


#### ⚡ Performance-Optimized Data Flow

The engine is designed for efficiency:

- Only **document IDs and scores** are processed in memory during ranking
- Full text content and snippets are **lazily loaded** from the database
- Data is fetched **only for the specific page** currently being viewed

This ensures low memory usage and high scalability, even for large corpora.


#### 📑 Efficient Pagination

- The engine processes **only document IDs** in memory
- Full text is fetched from **SQLite** only for the **10 results** displayed on the current page


#### 📈 Evaluation Metrics

The system measures search quality using:

- **Precision@5 (P@5)**  
→ Measures how many of the top 5 results are truly relevant

- **MRR (Mean Reciprocal Rank)**  
  → Evaluates where the first relevant result appears in the ranking

- **nDCG@5**  
  → Measures the quality of the ranking order based on graded relevance

## 🏁 Conclusion

The **Basic Search Engine NLP** project demonstrates the ground-up implementation of an **Information Retrieval system** that merges classic Natural Language Processing techniques with a modern, scalable software architecture.

By maintaining a clear separation between a high-performance **Python backend** and an interactive **Blazor frontend**, the system provides not just fast results, but also a platform for **testing and comparing ranking algorithms** (TF-IDF vs. BM25). The use of industry-standard metrics (**MRR**, **nDCG**, **Precision**) elevates this project from a simple search tool to a **professional framework** for evaluating and optimizing data relevance.

---

## 🌱 Future Developments

- [ ] **Phrase Search:** Implementing support for exact phrase matching (e.g., using `"quotation marks"`).  
- [ ] **Search History:** A dedicated module to track and display previous user queries.  
- [ ] **Contextual Highlighting:** Enhancing result cards to display the exact text segment where the search terms appear, rather than a fixed snippet.  
- [ ] **Semantic Search:** Integrating Sentence Embeddings (e.g., BERT) to understand query intent beyond keyword matching.
