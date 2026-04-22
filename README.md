# **Simulated Live Sports Betting Data Platform**

---

A production-style data engineering project that simulates live sports betting activity using batch and streaming pipelines.

It ingests NBA game data, simulated betting line updates, and simulated user betting events, processes them through a cloud-based data platform, and delivers analytics-ready datasets for reporting, monitoring, and business insights in Looker Studio.

---

## **Project Goal**

This project is designed to demonstrate a real-world data engineering workflow that supports both:

- **Live betting events** during active NBA games
- **Pregame betting lines** when games are not live

The platform is built to reflect production-style engineering practices, including streaming, batch processing, orchestration, transformation, testing, observability, governance, and analytics delivery.

---

## **Architecture Overview**

The system combines **streaming**, **batch ingestion**, **cloud warehousing**, **analytics engineering**, and **dashboard delivery**.

### **High-Level Flow**

1. **NBA API** provides real NBA schedule and game metadata
2. **Simulated sportsbook events** generate bets, odds updates, and game updates
3. **Kafka** captures real-time event streams
4. **Python ingestion jobs** load source and stream data into PostgreSQL
5. **Kestra** orchestrates ingestion and warehouse-loading workflows
6. **BigQuery** stores raw, staging, and curated analytical tables
7. **dbt** transforms raw warehouse data into business-ready models
8. **Looker Studio** visualizes sportsbook metrics for reporting and analysis

---

## **Architecture Components**

### **Data Sources**
- Real NBA game and schedule data from BallDontLie API
- Simulated user betting activity
- Simulated odds update events
- Simulated game state update events

### **Streaming Layer**
Kafka handles real-time event ingestion for:

- `bets`
- `odds_updates`
- `game_updates`

### **Batch Layer**
Batch pipelines are used for:

- NBA schedule and game metadata ingestion
- BigQuery warehouse loading
- analytics table generation
- scheduled orchestration via Kestra

### **Storage Layer**
Data moves through three layers:

- **Raw**: source and event-level warehouse tables
- **Staging**: cleaned dbt views on top of raw tables
- **Curated**: marts and aggregate tables for dashboard use

### **Warehouse Layer**
BigQuery stores all analytical tables used by dbt and Looker Studio.

### **Transformation Layer**
dbt builds:
- staging models for source cleanup
- mart models for core betting analytics
- aggregate models for dashboard metrics

### **Orchestration Layer**
Kestra manages:
- real NBA schedule ingestion
- warehouse refresh jobs
- repeatable task execution
- multi-step pipeline runs

### **Analytics Layer**
Looker Studio is used as the BI layer to surface:
- bet volume
- handle by game
- average stake
- market type mix
- odds movement
- live vs pregame bet mix

---

## **Tech Stack**

### **Core**
- Python
- SQL

### **Infrastructure**
- Docker
- Terraform
- GCP

### **Storage**
- PostgreSQL
- BigQuery
- Google Cloud Storage (provisioned for platform layer)

### **Streaming**
- Kafka
- Zookeeper

### **Processing**
- Python batch jobs
- Spark (reserved for larger-scale processing extension)

### **Orchestration**
- Kestra

### **Transformation**
- dbt

### **Analytics / BI**
- Looker Studio

### **CI / Collaboration**
- GitHub
- GitHub Actions

---

## **Repository Structure**

```text
project-root/
│
├── ingestion/
│   ├── api_clients/
│   ├── batch_jobs/
│   ├── producers/
│   └── schemas/
│
├── streaming/
│   ├── consumers/
│   ├── validators/
│   ├── transforms/
│   └── dlq/
│
├── orchestration/
│   └── kestra/
│
├── dbt/
│   └── sportsbook_dbt/
│       ├── models/
│       │   ├── staging/
│       │   └── marts/
│       ├── tests/
│       ├── macros/
│       └── dbt_project.yml
│
├── spark/
│   ├── jobs/
│   └── utils/
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfvars
│
├── dashboard/
│   └── looker_studio/
│
├── docs/
│   ├── architecture.md
│   ├── governance.md
│   ├── data_dictionary.md
│   ├── lineage.md
│   └── runbook.md
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── data_quality/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── docker-compose.kestra.yml
├── requirements.txt
├── README.md
└── .env.example
```

---

## **Data Model Overview**

The warehouse is organized around sportsbook-style analytics.

### **Core Mart Models**
- `dim_games`
- `fact_bets`
- `fact_odds_history`

### **Looker-Ready Aggregate Models**
- `agg_betting_activity_by_game`
- `agg_market_type_summary`
- `agg_odds_movement_by_game`
- `agg_live_vs_pregame_bet_mix`

These models support downstream reporting and dashboard analysis.

---

## **Governance and Privacy**

This project does **not** use real user data.

To reflect production-safe practices:
- all sportsbook users are simulated
- no personal information is stored
- raw, staging, and curated layers are separated
- warehouse transformations are reproducible
- event data is structured and traceable
- dbt models provide a controlled analytics layer

---

## **Observability and Quality**

The project includes basic production-style controls such as:
- repeatable ingestion scripts
- Kafka event separation by topic
- dbt modeling layers
- Kestra workflow logs
- warehouse verification queries
- reproducible infrastructure with Terraform

---

## **Prerequisites**

Install the following before starting:
- Python 3.11+
- Docker Desktop
- PostgreSQL
- Google Cloud SDK
- Terraform
- Java 17+
- dbt Core / `dbt-bigquery`

---

## **Environment Setup**

Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install dbt-bigquery
```

Create your environment file:

```bash
cp .env.example .env
```

Recommended `.env` values:

```env
POSTGRES_DB=sportsbook
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

KAFKA_BOOTSTRAP_SERVERS=localhost:9092

GCP_PROJECT_ID=de26-live-sportsbook-sim
GCS_BUCKET=de26-live-sportsbook-bucket
BIGQUERY_DATASET=de26_sportsbook_analytics

BALLDONTLIE_API_KEY=your_api_key_here
```

---

## **Infrastructure Setup**

### **Google Cloud Authentication**

Authenticate locally before using Terraform, dbt, or BigQuery loaders:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

### **Terraform**

From the `terraform/` directory:

```bash
terraform init
terraform plan
terraform apply
```

This provisions:
- GCS bucket
- BigQuery dataset

---

## **Start Local Services**

Start PostgreSQL, Zookeeper, and Kafka:

```bash
docker compose up -d
docker ps
```

Expected containers:
- `sportsbook_postgres`
- `sportsbook_zookeeper`
- `sportsbook_kafka`

---

## **Run the Core Pipeline**

### **1. Create local source tables in PostgreSQL**
Create the `raw` schema and source tables for:
- `raw.nba_games`
- `raw.bet_events_stream`
- `raw.odds_updates_stream`
- `raw.game_updates_stream`

### **2. Load initial NBA sample data**
```bash
python -m ingestion.batch_jobs.load_nba_schedule
```

### **3. Start Kafka event flow**
Run consumers first, then producers:

```bash
python -m streaming.consumers.bets_consumer
python -m streaming.consumers.odds_consumer
python -m streaming.consumers.game_updates_consumer
```

```bash
python -m ingestion.producers.bets_producer
python -m ingestion.producers.odds_producer
python -m ingestion.producers.game_updates_producer
```

### **4. Load raw tables into BigQuery**
```bash
python -m ingestion.batch_jobs.load_games_to_bigquery
python -m ingestion.batch_jobs.load_stream_tables_to_bigquery
```

### **5. Build dbt models**
Run dbt from the **correct project path**:

```bash
cd dbt/sportsbook_dbt
dbt debug
dbt run
```

### **6. Run orchestration in Kestra**
Start Kestra:

```bash
docker compose -f docker-compose.kestra.yml up -d
```

Open:
- `http://localhost:8080`

Run the `nba_schedule_ingestion` flow to:
- pull real NBA game data from BallDontLie API
- load refreshed games into PostgreSQL
- load refreshed games into BigQuery

---

## **Reproduction Steps**

To reproduce the project from scratch:

1. install prerequisites
2. clone the repository
3. create and activate `.venv`
4. install Python and dbt dependencies
5. configure `.env`
6. authenticate with GCP
7. run Terraform
8. start Docker services
9. create PostgreSQL raw tables
10. run initial batch ingestion
11. run Kafka producers and consumers
12. load raw tables into BigQuery
13. run dbt from `dbt/sportsbook_dbt`
14. start Kestra and run the orchestration flow
15. connect Looker Studio to the curated BigQuery tables

---

## **Dashboard**

The dashboard is publicly accessible at:

🔗 **View Live Dashboard**  
https://datastudio.google.com/reporting/e96ea5f4-9ab8-47f7-b99f-5f9e9b22c042

To connect your own BigQuery data to Looker Studio:

1. Go to `datastudio.google.com`
2. Click **Create** → **Report**
3. Click **Add data**
4. Choose **BigQuery**
5. Select:
   - project: `de26-live-sportsbook-sim`
   - dataset: `de26_sportsbook_analytics`
6. Add these tables one by one:
   - `agg_betting_activity_by_game`
   - `agg_market_type_summary`
   - `agg_odds_movement_by_game`
   - `agg_live_vs_pregame_bet_mix`

### **Dashboard Contents**

The dashboard is designed around the following metric tables:

| Chart / View | Recommended Type | Source Table | Insight |
|---|---|---|---|
| Betting Activity by Game | Bar chart / table | `agg_betting_activity_by_game` | Total bets, handle, and average stake by game |
| Market Type Summary | Bar chart / donut chart | `agg_market_type_summary` | Shows which bet markets drive volume |
| Odds Movement by Game | Table / scorecard mix | `agg_odds_movement_by_game` | Tracks min/max odds and update count |
| Live vs Pregame Bet Mix | Donut / bar chart | `agg_live_vs_pregame_bet_mix` | Splits handle and bet count by timing |

Suggested scorecards:
- total bets
- total handle
- average stake
- number of games with betting activity

---

## **Development Notes**

### **Orchestration Notes**
Kestra runs inside its own container, so local assumptions do not always carry over. Two important differences:

- `source .venv/bin/activate` fails because Kestra shell tasks use `sh`, not `bash`
- `localhost` inside Kestra refers to the Kestra container itself, not PostgreSQL

That means:
- use direct Python execution inside the task
- use `POSTGRES_HOST=sportsbook_postgres` for container-to-container access

### **Google Credentials in Kestra**
BigQuery loading from Kestra requires Google credentials **inside the container**, not just on your laptop. The reliable approach is:
- mount `application_default_credentials.json` into the container
- set `GOOGLE_APPLICATION_CREDENTIALS` in `docker-compose.kestra.yml`

Without this, BigQuery client creation fails even if `bq` works locally.

### **BallDontLie API Notes**
The correct API base is:
- `https://api.balldontlie.io/v1/games`

Important details:
- the old `www.balldontlie.io/api/v1/...` route returned `404`
- the current API requires an `Authorization` header and API key after creating an account
- missing or invalid API keys cause `401 Unauthorized`

### **BigQuery Load Method**
`google-cloud-bigquery`'s `load_table_from_dataframe()` requires `pyarrow`, which caused repeated install and hash problems in the Kestra container. The project avoids that by:
- exporting the pandas DataFrame to a temporary CSV
- loading with `load_table_from_file()`

This makes the pipeline more stable and easier to reproduce across environments.

### **dbt Project Path**
A major gotcha is running dbt from the wrong folder.

Use:

```bash
cd dbt/sportsbook_dbt
dbt run
```

Do **not** run dbt from an unintended duplicate project folder, or dbt may rebuild default boilerplate models instead of the sportsbook models.

### **Container Networking**
For the local multi-container stack to work cleanly:
- PostgreSQL, Kafka, Zookeeper, and Kestra should share the same Docker network
- service names, not localhost, should be used for inter-container communication

### **Cost / Read Performance**
The model strategy is intentionally simple:
- **raw tables** store loaded source data
- **staging models** are views used for cleanup and standardization
- **mart and aggregate models** are tables used by Looker Studio

This keeps dashboard reads fast because the BI layer reads from already-aggregated BigQuery tables rather than scanning raw event tables every time.

---

## **Troubleshooting Tips**

### **If Kestra says `source: not found`**
Kestra shell tasks use `sh`, not `bash`. Do not rely on `source .venv/bin/activate`.

### **If Kestra cannot reach Postgres**
Check:
- shared Docker network exists
- `POSTGRES_HOST=sportsbook_postgres`
- password matches the actual running PostgreSQL container

### **If BigQuery auth fails in Kestra**
Check:
- ADC file is mounted into the container
- `GOOGLE_APPLICATION_CREDENTIALS` points to it
- `gcloud auth application-default login` was completed locally first

### **If BallDontLie returns 401**
Check:
- `BALLDONTLIE_API_KEY` is present in `.env`
- the same key is available in Kestra container env
- the request uses the current API domain and authorization header

### **If dbt builds boilerplate models**
You are almost certainly running dbt from the wrong folder.

Use:

```bash
cd dbt/sportsbook_dbt
```

### **If Looker tables do not appear**
Make sure you are connecting Looker Studio to the **aggregate tables**, not the raw or staging layers.

---

## **Current Scope**

### **Included in MVP**
- NBA data only
- real NBA schedule/game ingestion
- simulated live betting events
- simulated odds and game update streams
- Kafka event ingestion
- PostgreSQL source/event storage
- BigQuery warehouse models
- dbt marts and aggregate tables
- Kestra orchestration
- Looker Studio dashboards

### **Planned Expansion**
- additional sports leagues
- richer bet types
- true live odds API integration
- more advanced observability
- CI/CD validation
- dbt tests and documentation expansion
- stronger governance and lineage docs
