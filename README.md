# PrismX – Hybrid RAG Legal AI Assistant ⚖️

PrismX is a production-grade, end-to-end Legal AI Assistant designed for Indian law.
It uses a Hybrid RAG architecture combining dense vector search and a Cache-Augmented Generation (CAG) layer.
[**DEMO**](https://drive.google.com/drive/folders/1lhRU69krTxgMOfo-ETYth_EhKDyUzZ02)

## 🚀 Key Features
- Hybrid retrieval engine with CAG and RAG.
- Hallucination-proofing with strict citation grounding.
- FastAPI backend, React frontend, Docker ready.

## 🧠 Architecture
PrismX uses a Dual-Path Retrieval System:

- User Query: "What is the punishment for murder under BNS?"

- Path A (CAG): Regex detects "murder" and "BNS". Instantly  fetches Section 103 from the in-memory JSON cache. (Score: 1.0)

- Path B (RAG): Encoder converts query to vector. FAISS retrieves top-k relevant case judgments from SQLite. (Score: 0.7-0.9)

- Hybrid Merge: The system prioritizes the Statute (CAG) and appends relevant Case Laws (RAG).

- Generation: Gemini 2.5 Flash synthesizes the answer, citing specific Document IDs.

```mermaid
graph TD
    A[User Query] --> B{Router};
    B -- "Statute Citation?" --> C[CAG Cache (Redis/Dict)];
    B -- "Semantic Search" --> D[Jina Embeddings];
    D --> E[FAISS Index];
    E --> F[SQLite DB (Chunks)];
    C --> G[Context Window];
    F --> G;
    G --> H[Gemini 2.5 Flash];
    H --> I[Final Answer];

```

## 🧰 Tech Stack
- LLM: Google Gemini 2.5 Flash

- Backend: Python, FastAPI, Uvicorn

- Frontend: React.js, Tailwind CSS, Framer Motion, Lucide React

- Vector DB: FAISS (CPU optimized)

- Embeddings: jinaai/jina-embeddings-v2-base-en (8192 token context)

- Storage: SQLite (Text Chunks), JSON (Statute Cache)
- Deployment: Docker and AWS App Runner

## 📊 Performance Benchmarks
## 📊 Performance Metrics

Benchmarked on a synthetic **"Golden Dataset"** of 50 complex legal queries using an **LLM-as-a-Judge** evaluator.

| **Metric**            | **Phase 1 (Base RAG)** | **Phase 2 (Hybrid RAG+CAG)** | **Improvement**      |
|----------------------|-------------------------|-------------------------------|------------------------|
| **Citation Accuracy** | 82%                     | 99.80%                          | **+18%**              |
| **Faithfulness**      | 0.83                    | 0.95                          | **+0.12**             |
| **Hallucination Rate**| 0.20                    | 0.07                          | **-30% (Better)**     |
| **Avg Latency**       | 375ms                   | 291ms                         | **-18% (Faster)**      |


## ⚙️ Installation
### Backend Setup
```bash
git clone https://github.com/Rudra-200/prismx-legal-ai.git
cd prismx-legal-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_api_key_here" > .env
python app.py
```
Backend will start at http://localhost:8000

### FrontendSetup
```bash
cd frontend
npm install
npm run dev
```
Frontend will start at http://localhost:5173
## 🐳 Docker Deployment
Build and run the entire backend as a single container.
```bash
docker build -t legal-rag-api .
docker run -p 8000:8000 --env-file .env legal-rag-api
```

## 📂 Structure
```
.
├── app.py                 # FastAPI Entry Point
├── core/
│   ├── config.py          # App Configuration
│   ├── retrieval.py       # Hybrid Retriever Logic
│   ├── database.py        # SQLite Handler
│   └── ingestion.py       # PDF Parsing Pipeline
├── artifacts/             # Data Storage (GitIgnored)
│   ├── chunks.db          # Text Database
│   ├── faiss_index.bin    # Vector Index
│   └── statute_cache.json # CAG Lookup Table
├── frontend/              # React Application
└── Dockerfile             # Production Build
```

## 📜 License
Copyright (C) 2025  Rudra Prasanna Mishra

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

## 📞 Contacts
Rudra Prasanna Mishra @mishrarudra.work@gmail.com
