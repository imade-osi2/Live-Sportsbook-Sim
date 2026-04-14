# **Simulated Live Sports Betting Data Platform**

---

A production-style data engineering project that simulates live sports betting activity using batch and streaming pipelines.

It ingests NBA game, betting line, and user betting events, processes them through a cloud-based data platform, and delivers analytics-ready datasets for reporting, monitoring, and business insights.

---

## **Project Goal**

This project is designed to demonstrate a real-world data engineering workflow that supports both:

- **Live betting events** during active NBA games
- **Pregame betting lines** when games are not live

The platform is built to reflect production-style engineering practices, including streaming, batch processing, orchestration, transformation, testing, observability, governance, and analytics delivery.

---

## **Architecture Overview**

The system is built around both **streaming** and **batch** pipelines.

### **High-Level Flow**

1. **NBA data sources** provide game schedules, scores, live updates, and betting lines
2. **Simulated user betting events** generate fake sportsbook activity
3. **Kafka** captures real-time event streams
4. **Python and Spark jobs** process and validate incoming data
5. **GCS** stores raw and intermediate data in the data lake
6. **BigQuery** stores structured warehouse tables for analytics
7. **dbt** transforms raw data into business-ready models
8. **Kestra** orchestrates ingestion and transformation workflows
9. **Looker Studio** visualizes final metrics for reporting and analysis

---

## **Architecture Components**

### **Data Sources**
- NBA schedules and game results
- Live NBA game updates
- Pregame betting line snapshots
- Simulated user betting activity

### **Streaming Layer**
Kafka is used to handle real-time event ingestion for:

- `bets`
- `odds_updates`
- `game_updates`
- `line_snapshots`

### **Batch Layer**
Batch pipelines are used for:

- historical schedule ingestion
- full refreshes of reference data
- large-volume transformations
- analytics table generation

### **Storage Layer**
Data moves through three layers:

- **Raw**: unprocessed source events and files
- **Staging**: cleaned and standardized records
- **Curated**: analytics-ready data models

### **Warehouse Layer**
BigQuery stores structured analytical tables used by downstream models and dashboards.

### **Transformation Layer**
dbt is used to build and test analytics-ready models such as:

- `fact_bets`
- `fact_odds_history`
- `fact_games`
- `dim_users`
- `dim_teams`
- `dim_games`

### **Orchestration Layer**
Kestra schedules and manages:

- ingestion jobs
- retries
- dependencies
- backfills
- transformation workflows

### **Analytics Layer**
Looker Studio is used as the reporting layer to surface business metrics such as:

- bet volume
- win rate
- odds movement
- line movement
- live vs pregame betting mix
- payout and exposure by game

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
- Google Cloud Storage (GCS)
- BigQuery

### **Streaming**
- Kafka

### **Processing**
- Apache Spark

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
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   └── macros/
│
├── spark/
│   ├── jobs/
│   └── utils/
│
├── terraform/
│   ├── modules/
│   └── environments/
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
├── requirements.txt
├── README.md
└── .env.example
```

---

## **Data Model Overview**

The warehouse is organized around sportsbook-style analytics.

### **Fact Tables**
- `fact_bets`
- `fact_odds_history`
- `fact_games`

### **Dimension Tables**
- `dim_users`
- `dim_teams`
- `dim_games`

These models support downstream analytics and dashboard reporting.

---

## **Governance and Privacy**

This project does **not** use real user data.

To reflect production-safe practices:

- all users are simulated
- user identifiers are hashed
- no personal information is stored
- raw, staging, and curated layers are separated
- schema validation checks are applied
- data quality tests are included
- lineage and data definitions are documented

---

## **Observability and Quality**

The project includes basic production-style controls such as:

- schema validation for event payloads
- dbt model tests
- logging for pipeline runs
- record count checks
- invalid event handling
- documentation for data lineage and runbooks

---

## **Local Setup**

### **Prerequisites**

Install the following before starting:

- Python 3.11+
- Docker Desktop
- PostgreSQL
- Google Cloud SDK
- Terraform
- Java 17+
- Apache Kafka
- Apache Spark
- dbt Core

---

## **Environment Setup**

Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Update `.env` with your local and cloud configuration values.

---

## **Google Cloud Setup**

Authenticate with Google Cloud:

```bash
gcloud auth application-default login
gcloud auth login
```

Set your project:

```bash
gcloud config set project YOUR_GCP_PROJECT_ID
```

Create or verify:

- GCS bucket
- BigQuery dataset
- service account permissions

If using Terraform, these resources will be provisioned automatically.

---

## **Infrastructure Setup**

From the `terraform/` directory:

```bash
terraform init
terraform plan
terraform apply
```

This should provision the core cloud infrastructure such as:

- GCS bucket(s)
- BigQuery dataset(s)
- related cloud resources for the project

---

## **Start Local Services**

Use Docker Compose to start local services such as PostgreSQL and Kafka:

```bash
docker-compose up -d
```

Confirm containers are running:

```bash
docker ps
```

---

## **Run the Initial Pipelines**

### **1. Ingest NBA reference and schedule data**
```bash
python ingestion/batch_jobs/load_nba_schedule.py
```

### **2. Start Kafka producers**
```bash
python ingestion/producers/bets_producer.py
python ingestion/producers/odds_producer.py
python ingestion/producers/game_updates_producer.py
```

### **3. Start Kafka consumers**
```bash
python streaming/consumers/bets_consumer.py
python streaming/consumers/odds_consumer.py
python streaming/consumers/game_updates_consumer.py
```

### **4. Run Spark processing jobs**
```bash
spark-submit spark/jobs/process_betting_events.py
```

### **5. Run dbt models**
```bash
cd dbt
dbt deps
dbt seed
dbt run
dbt test
```

### **6. Trigger orchestration flows**
Run Kestra flows for scheduled ingestion and transformation jobs.

---

## **Dashboard Setup**

After warehouse tables and dbt models are built:

1. Connect **Looker Studio** to BigQuery
2. Use curated models as data sources
3. Build dashboards for:
   - bet volume
   - win rate
   - line movement
   - odds movement
   - live vs pregame betting mix
   - payout / exposure by game

---

## **Reproduction Steps**

To reproduce the project from scratch:

1. install prerequisites
2. clone the repo
3. configure `.env`
4. authenticate with GCP
5. run Terraform
6. start Docker services
7. run ingestion jobs
8. start Kafka producers and consumers
9. run Spark jobs
10. build dbt models
11. connect Looker Studio to BigQuery

---

## **Current Scope**

### **Included in MVP**
- NBA data only
- live betting events
- pregame betting lines
- batch + streaming pipelines
- cloud warehouse models
- Looker Studio dashboards

### **Planned Expansion**
- additional sports leagues
- richer bet types
- more advanced observability
- broader analytics coverage
