# 📈 Job Market Skill Demand Analyzer & Intelligence Crawler

An enterprise-grade, ethical web crawling and natural language processing platform that tracks, normalizes, and visualizes real-time tech labor market skill demand, compensation benchmarks, and hiring trends.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    subgraph Data Sources
        A1[Arbeitnow Public Tech Feed]
        A2[RemoteOK API]
        A3[Jobicy Tech API]
        A4[Greenhouse Career Boards]
        A5[Mock Portal Test Suite]
    end

    subgraph Crawler Engine & Politeness
        F[Crawl Frontier Queue]
        P[Politeness & Rate Limiter\n(robots.txt, delays, circuit breaker)]
        E[Crawl Engine Orchestrator]
    end

    subgraph Data Processing Pipeline
        D[Deduplication Fingerprinting\n(SHA-256 Content Hashing)]
        TN[Title & Seniority Normalizer]
        SE[NLP Skill & Requirement Extractor\n(7 Categories, Required vs Preferred)]
    end

    subgraph Storage Layer
        DB[(PostgreSQL Database\nFallback: SQLite)]
    end

    subgraph Application & Presentation
        API[FastAPI Backend\nREST Analytics & Telemetry]
        DASH[Streamlit Interactive Dashboard\nPlotly Visualizations & Filters]
    end

    A1 & A2 & A3 & A4 & A5 --> F
    F --> P --> E
    E --> D --> TN --> SE --> DB
    DB --> API
    DB --> DASH
```

---

## ✨ Key Capabilities

1. **Ethical & Polite Crawling Engine**:
   - **Robots.txt Adherence**: Parses and respects `robots.txt` disallow rules per domain.
   - **Per-Domain Rate Limiting**: Configurable download delays (default: 2.0s).
   - **Adaptive Exponential Backoff & Circuit Breakers**: Automatically backs off on HTTP 429/503 and pauses domain requests if rate limits persist.
   - **Frontier Queue Management**: Priority queuing, depth tracking, canonical URL deduplication.

2. **NLP & Market Intelligence Pipeline**:
   - **7-Category Skill Taxonomy**: Languages, Frameworks, Cloud/DevOps, Databases, AI/ML, Tools, and Soft Skills.
   - **Qualification Classification**: Distinguishes **Must-Have Requirements** from **Preferred / Nice-to-Have Pluses**.
   - **Role & Seniority Standardization**: Maps non-standard titles into canonical categories (`Backend Developer`, `Machine Learning Engineer`, `Data Engineer`, `DevOps / SRE`, etc.) and seniority tiers (`Entry-Level`, `Mid-Level`, `Senior`, `Lead / Staff`).
   - **Salary Extraction**: Automatic regex and text parsing of compensation ranges, normalized to annual USD equivalents.

3. **High-Performance Storage**:
   - Dual-mode database layer: Seamlessly connects to **PostgreSQL**, with zero-config graceful fallback to local **SQLite** (`job_market.db`).
   - Granular audit logging (`crawl_logs`) and execution performance telemetry (`crawl_runs`).

4. **FastAPI REST API**:
   - Market overview KPIs, top skills leaderboard, role-skill matrix cross-tabulations.
   - Skill co-occurrence network analysis with Jaccard similarity metrics.
   - Global tech hubs and salary distributions.
   - Full crawler control and background execution triggers.

5. **Interactive Streamlit Dashboard**:
   - Modern dark/sleek theme with glassmorphic metric cards and Plotly charts.
   - Multi-tab exploration: Executive Overview, Skill Rankings, Role-Skill Matrix, Emerging Tech Momentum, Global Tech Hubs, Live Crawler Operations, and Full-Text Job Explorer with CSV Export.

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*Note: If PostgreSQL is not running locally, the system automatically falls back to SQLite without any configuration required.*

### 3. Seed Realistic Market Data
Populate the platform with diverse tech job requisitions across multiple roles and hubs:
```bash
python scripts/seed_data.py
```

### 4. Run the Crawler CLI
Run ethical crawlers directly from the terminal:
```bash
# Run 2 pages using the local mock test suite
python scripts/run_crawler.py --source mock --pages 2

# Crawl live authorized tech feed
python scripts/run_crawler.py --source arbeitnow --pages 3
```

### 5. Launch the FastAPI Backend
Start the REST API server:
```bash
uvicorn api.main:app --reload --port 8000
```
Interactive Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 6. Launch the Interactive Dashboard
Start the Streamlit analytics application:
```bash
streamlit run dashboard/app.py --server.port 8501
```
Open in browser: [http://localhost:8501](http://localhost:8501)

---

## 🧪 Testing

Run the comprehensive unit and integration test suite:
```bash
pytest -v
```
All 24 test cases validate:
- Skill taxonomy regex and NLP requirement classification
- Title normalization and experience extraction
- Politeness, robots.txt, rate limiting, and circuit breaker logic
- Content fingerprinting and deduplication filters
- FastAPI REST endpoints and database repository aggregations

---

## 📁 Repository Structure

```
├── api/
│   ├── main.py              # FastAPI application entrypoint & middleware
│   ├── routes_analytics.py  # Market intelligence and aggregation endpoints
│   ├── routes_crawler.py    # Crawler control, logs, and telemetry endpoints
│   ├── routes_jobs.py       # Job search, details, and CSV export endpoints
│   └── schemas.py           # Pydantic request/response data contracts
├── config/
│   └── settings.py          # Environment settings and crawler thresholds
├── crawler/
│   ├── adapters/            # Portal adapters (Arbeitnow, RemoteOK, Greenhouse, Mock, etc.)
│   ├── deduplication.py     # Content SHA-256 fingerprinting & Jaccard similarity
│   ├── engine.py            # Orchestrator coordinating crawl lifecycle
│   ├── frontier.py          # Priority queue & canonical URL normalizer
│   ├── pipelines.py         # End-to-end cleaning and ingestion pipeline
│   └── politeness.py        # Robots.txt parser, rate limiter & circuit breaker
├── dashboard/
│   └── app.py               # Streamlit analytics dashboard
├── database/
│   ├── connection.py        # SQLAlchemy engine (PostgreSQL + SQLite fallback)
│   ├── models.py            # ORM tables (Job, Skill, JobSkill, CrawlRun, etc.)
│   └── repository.py        # CRUD queries & SQL analytics aggregations
├── nlp/
│   ├── analytics.py         # Co-occurrence and Jaccard association calculations
│   ├── skill_extractor.py   # Regex extraction & Required vs Preferred classifier
│   ├── taxonomy.py          # Comprehensive 7-category skill taxonomy
│   └── title_normalizer.py  # Canonical role mapping & experience parser
├── scripts/
│   ├── run_crawler.py       # Command line interface for crawler execution
│   └── seed_data.py         # High-fidelity dataset seeder
├── tests/                   # 24 Unit & Integration tests
├── schema.sql               # PostgreSQL DDL schema & analytical views
└── requirements.txt         # Project dependencies
```
