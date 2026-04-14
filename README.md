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