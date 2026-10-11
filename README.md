# CropShield AI — Agriculture Crop Advisory Assistant

CropShield AI is a local decision-support application for exploring historical crop cases, getting crop recommendations, estimating yield, and reviewing agronomic risk. It combines a FastAPI service, hybrid case retrieval, tabular machine-learning models, an orchestrated advisory workflow, and a dark-green browser dashboard.

## Problem and objective

Farm decisions depend on crop, soil, climate, season, location, and input conditions. Searching historical cases manually is slow, while ungrounded generative answers can overstate certainty. CropShield AI brings case retrieval, model estimates, risk context, and an advisory response into one workflow for agronomists and agricultural extension users. Outputs are decision support; they are not a substitute for local agronomic review.

## Project implementation

- **Language and runtime:** Python 3.12; the project also runs on compatible recent Python versions.
- **API:** FastAPI, Pydantic, Uvicorn. OpenAPI UI is available at `/docs`.
- **Primary frontend:** HTML, CSS, and JavaScript in `frontend/`, served by FastAPI. A separate Streamlit client is also present at `frontend/frontend.py`.
- **Retrieval:** FAISS CPU vector index plus keyword and metadata search with hybrid ranking. The default dense representation uses scikit-learn `HashingVectorizer` features followed by a seeded local projection. This is a local deterministic representation, not a downloaded pretrained embedding model.
- **LLM:** Optional OpenAI-compatible chat/judge provider, configured with `OPENAI_BASE_URL`, `LLM_MODEL`, and `OPENAI_API_KEY`. Live RAGAS/DeepEval judge calls require an accessible compatible provider and sufficient account credits.
- **Machine learning:** scikit-learn Random Forest yield regressor and crop-suitability classifier, using categorical and agronomic numeric features.
- **Persistence:** CSV data, local model files, FAISS/index files, SQLite user database, and JSON feedback/evaluation reports.
- **Vector database:** FAISS is implemented. ChromaDB is not present in the inspected source.

## Data and evaluation

The application sample at `data/sample/sample_crop_data.csv` contains 1,500 rows of **locally generated synthetic test data**. It has no external dataset source link or verified field provenance. Processed records and features are in `data/processed/processed_data.csv`. Do not present the sample as a field survey or government dataset.

Saved reports are under `evaluation/reports/`. The latest saved retrieval benchmark includes 20 labeled queries and reports Precision@1/3/5, Recall@5, MRR, and Hit Rate@5. ML reports use a held-out split from the synthetic dataset. RAGAS and DeepEval are supported by evaluation modules, but their scores depend on a reachable, configured judge provider; review the evaluation page and `docs/Evaluation_Report.pdf` for saved status and limitations. A failed or unavailable live judge call must not be described as a successful evaluation.

## Setup

Open PowerShell in the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

If the virtual environment already exists, activate it and install dependencies with `pip install -r requirements.txt`.

### Environment configuration

`.env.example` contains placeholders only. Set values in your local, untracked `.env` file:

- `OPENAI_API_KEY`: optional provider key. Keep it private. Leave unset for local retrieval and ML features; live generation/judge evaluation may be unavailable.
- `OPENAI_BASE_URL`: OpenAI-compatible API base URL.
- `LLM_MODEL`: chat and judge model name supported by the configured provider.
- `EMBEDDING_PROVIDER`: defaults to `dense_local`; optional provider choices are defined in `app/rag/embeddings.py` and settings. The default `EMBEDDING_MODEL` is not downloaded when local mode is used.
- `HOST`, `PORT`: FastAPI bind address and port.
- `INITIAL_USER_EMAIL`, `INITIAL_USER_PASSWORD`, `INITIAL_USER_NAME`, `INITIAL_USER_ROLE`: optional first-account bootstrap values. They default blank (except the descriptive name) and are read only when the database initializes. Alternatively, create an account through the application signup page. Never commit real credentials.
- `CROPSHIELD_API_URL`: optional Streamlit client backend URL; defaults to `http://localhost:8000`.

The existing `.env` is not included in this submission. `.gitignore` excludes it and the local SQLite account database.

## Run locally

### FastAPI and primary dashboard

```powershell
python run.py
```

Open <http://127.0.0.1:8000/> for the dashboard, <http://127.0.0.1:8000/docs> for API documentation, or <http://127.0.0.1:8000/health> for the health check. The FastAPI startup initializes the local user database and loads/builds missing indexes or models from the configured local data.

Alternatively:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Optional Streamlit client

Run the API in one terminal, then run:

```powershell
streamlit run frontend/frontend.py --server.port 8501
```

Open <http://localhost:8501>. Set `CROPSHIELD_API_URL` if the API uses another host/port. The primary supported browser UI remains the FastAPI-served SPA.

## Example agricultural queries

Try these in the advisory query screen. The response format includes an interpreted intent, crop recommendations, similar historical cases, and applicable risk/yield/impact analysis; exact results depend on retrieved cases and model outputs.

1. “Which crops are suitable for Kharif in Andhra Pradesh with pH 6.5 and rainfall around 1,000 mm?”
2. “Show historical Wheat cases from Punjab during Rabi and compare their yields.”
3. “I have N=80, P=40, K=35 and soil pH 6.5. Which crops should I consider?”
4. “Suggest alternatives to Cotton in Gujarat for the current season.”
5. “Estimate Rice yield in Andhra Pradesh with 1,100 mm rainfall, pH 6.5, and 28°C.”

Typical response sections are: **recommendations** (crop labels and suitability/context), **similar cases** (case identifiers, conditions, outcomes, relevance), **risk analysis**, **yield prediction** where applicable, **formatted advisory**, and **limitations**. These are response-shape examples, not promised values or agronomic guarantees.

## Tests and evaluation

Run the existing test suite:

```powershell
python -m pytest -q
```

Regenerate the submission PDFs and slide deck from local project artifacts:

```powershell
python scripts/generate_capstone_submission.py
```

The generator reads the saved report JSON files and current CSV schema. It does not call an external LLM or fabricate missing judge results.

## Submission documents

- [Architecture diagram](architecture/Architecture_Diagram.pdf)
- [Design document](design/Design_Document.pdf)
- [API documentation](docs/API_Documentation.pdf)
- [Dataset details](docs/Dataset_Details.pdf)
- [Evaluation report](docs/Evaluation_Report.pdf)
- [10-minute project presentation](presentation/Project_Presentation.pptx)
- [Source layout map](src/README.md)

## Repository layout notes

The requested submission `src/` directories map to the application's canonical `app/` package. The original implementation is intentionally left in place because imports, settings, tests, data paths, model paths, and index persistence depend on it. `src/main.py` is a thin alternate launcher. Similarly, the application reads sample data from `data/sample/`; `data/sample_data/README.md` documents that canonical path instead of duplicating the dataset. See the architecture and dataset PDFs for component details.

## Troubleshooting

- **`py` or `python` is not found:** install Python 3.12 and enable the Windows Python launcher, or invoke the interpreter at `.venv\Scripts\python.exe`.
- **Port 8000 is occupied:** stop the other service or change the port in local `.env`, then set the same API URL for Streamlit.
- **Streamlit command is missing:** activate `.venv` and run `pip install -r requirements.txt`.
- **Login fails on a fresh database:** sign up using the main application, or set the optional bootstrap environment values before the first database initialization. A pre-existing local `data/users.db` is retained.
- **LLM or RAGAS/DeepEval errors:** local retrieval and ML do not require a cloud judge. Check provider URL/model compatibility, server network access, key validity and account credits. The UI reports unavailable/error rather than a measured score when the provider fails.
- **Indexes or models are missing:** startup attempts to build/train them from the local data; review console logs and confirm data, write permissions and installed requirements.
- **Dataset metrics look unusually strong:** the included data are synthetic test records; validate on independently sourced, licensed and representative data before using results for real farming decisions.

## Important implementation notes

No Docker files are changed by this submission. No external dataset provenance is claimed. The system has FAISS rather than ChromaDB, row-based case indexing rather than a separate chunking pipeline, and a primary static SPA plus an optional Streamlit client. Evaluation claims in the PDFs are tied to checked-in JSON artifacts or explicitly marked pending.
