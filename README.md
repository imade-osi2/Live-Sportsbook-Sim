# **Live & Pre-Game Sports Betting Analytics Platform**

---

A production-style data engineering project that ingests real NBA events, bookmaker odds, and score data, transforms them into analytics-ready warehouse models, and publishes a live sportsbook-style reporting layer in Looker Studio.

The platform is built to answer practical betting-market questions such as:
- what games are currently on the board
- which bookmakers have the best available prices
- how prices differ across books
- which matchups show stronger value signals
- how pre-game and live market states differ over time

---

## **Project Goal**

This project demonstrates a real-world sports data platform that combines:

- **real NBA event data**
- **real bookmaker odds**
- **real score / game-state data**
- **warehouse modeling for market analysis**
- **dashboard delivery for decision support**

The focus is not on real bettor wager feeds. Instead, the platform is designed to track the market itself and surface useful betting-oriented metrics such as:
- latest moneyline prices by bookmaker
- number of active games
- number of tracked bookmakers
- suggested value opportunities
- expected value and edge signals
- game state context (pregame, live, final)
- evaluation of suggested plays against later observed prices

---

## **Architecture Overview**

The platform combines API ingestion, local storage, cloud warehousing, analytics engineering, orchestration, and BI delivery.

### **High-Level Flow**

1. **The Odds API** provides real NBA events, odds, and scores
2. **Python ingestion jobs** load raw market data into PostgreSQL
3. **BigQuery loaders** move those raw tables into the analytics warehouse
4. **dbt** builds staging, mart, and aggregate models for reporting
5. **Kestra** orchestrates repeatable refresh workflows
6. **Looker Studio** reads the curated models and displays live and pre-game market analytics

---

## **Architecture Components**

### **Market Data Sources**
- NBA event schedule and event IDs
- real bookmaker odds for moneyline, spreads, and totals
- live and completed score updates
- bookmaker-specific price snapshots across multiple books

### **Storage Layer**
Data is persisted across:
- **PostgreSQL** for local ingestion and operational staging
- **BigQuery** for warehouse modeling and dashboard consumption

### **Transformation Layer**
dbt is used to build:
- source cleanup models
- event and odds fact tables
- game-level market board models
- suggestion / evaluation models
- dashboard aggregates

### **Orchestration Layer**
Kestra is used to:
- manually refresh market data
- run end-to-end update flows
- automate warehouse refreshes later if desired

### **Analytics Layer**
Looker Studio surfaces:
- overview KPIs
- live market board
- suggested bets board
- evaluation board
- research board

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
- Google Cloud Storage

### **Streaming / Platform Support**
- Kafka
- Zookeeper

### **Transformation**
- dbt

### **Orchestration**
- Kestra

### **Analytics / BI**
- Looker Studio

### **Version Control**
- GitHub

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
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── terraform.tfvars
│
├── dashboard/
│   └── looker_studio/
│
├── docs/
│
├── docker-compose.yml
├── docker-compose.kestra.yml
├── requirements.txt
├── README.md
└── .env.example
```

---

## **Current Data Model**

The warehouse is now centered around real market data and dashboard-ready betting analytics.

### **Core Real Market Models**
- `dim_events`
- `fact_real_odds_history`
- `fact_real_scores`

### **Live Market / Dashboard Models**
- `agg_latest_real_odds_by_game`
- `agg_live_market_board`
- `agg_platform_kpis`

### **Suggestion / Evaluation Models**
- `fact_bet_suggestions`
- `agg_suggested_bets_board`
- `fact_bet_evaluation`
- `agg_clv_summary`
- `agg_suggestion_performance_summary`

### **Research / Context Models**
- `fact_game_research_signals`
- `agg_research_board`

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

GCP_PROJECT_ID=your_gcp_project_id
GCS_BUCKET=your_bucket_name
BIGQUERY_DATASET=de26_sportsbook_analytics

BALLDONTLIE_API_KEY=your_balldontlie_key
THE_ODDS_API_KEY=your_the_odds_api_key
THE_ODDS_SPORT=basketball_nba
THE_ODDS_REGIONS=us
THE_ODDS_MARKETS=h2h,spreads,totals
```

---

## **Infrastructure Setup**

### **Google Cloud Authentication**

Authenticate locally before using Terraform, loaders, or dbt:

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

This provisions the core GCP resources used by the warehouse.

---

## **Start Local Services**

Start the local stack:

```bash
docker compose up -d
docker ps
```

Expected containers:
- `sportsbook_postgres`
- `sportsbook_zookeeper`
- `sportsbook_kafka`

Start Kestra separately when needed:

```bash
docker compose -f docker-compose.kestra.yml up -d
```

---

## **Run the Core Market Pipeline**

### **1. Pull real NBA event, odds, and score data**
```bash
python -m ingestion.batch_jobs.load_nba_events_api
python -m ingestion.batch_jobs.load_nba_odds_api
python -m ingestion.batch_jobs.load_nba_scores_api
```

### **2. Load raw market tables into BigQuery**
```bash
python -m ingestion.batch_jobs.load_nba_market_tables_to_bigquery
```

### **3. Build dbt models**
Always run dbt from the correct project path:

```bash
cd dbt/sportsbook_dbt
dbt debug
dbt run
```

### **4. Refresh the full pipeline manually with Kestra**
Use the manual refresh flow in Kestra to:
- refresh events
- refresh odds
- refresh scores
- load raw market tables to BigQuery
- rebuild dbt models

---

## **Dashboard**

The dashboard is publicly accessible at:

🔗 **View Live Dashboard**  
https://datastudio.google.com/reporting/e96ea5f4-9ab8-47f7-b99f-5f9e9b22c042

The current dashboard presents a sportsbook-style operating view built around live and pre-game odds rather than raw ingestion tables. Current top-line metrics include:
- **active_games = 10**
- **bookmakers_tracked = 9**
- **total_suggestions = 506**
- **avg_expected_value = 0.03**
- **avg_edge = 0.01**
- **high_confidence_suggestions = 41**

---

## **Dashboard Pages and Metrics**

### **1. Overview**
Primary source tables:
- `agg_platform_kpis`
- `agg_research_board`
- `agg_suggestion_performance_summary`

Key metrics:
- active games
- bookmakers tracked
- total suggestions
- high-confidence suggestions
- average expected value
- average edge
- research board sorted by strongest signals

This page gives the quickest read on how many markets are available and how many current opportunities are being surfaced.

### **2. Live Market Board**
Primary source table:
- `agg_live_market_board`

Key fields:
- `game_date`
- `matchup`
- `game_state`
- `bookmaker_title`
- `outcome_name`
- `latest_h2h_price`
- `away_score`
- `home_score`

This board is the market view: it shows the currently available moneyline prices by bookmaker for each matchup and whether the game is still pregame, live, or final.

### **3. Suggested Bets Board**
Primary source table:
- `agg_suggested_bets_board`

Key fields:
- `game_date`
- `matchup`
- `game_state`
- `bookmaker_title`
- `outcome_name`
- `confidence_tier`
- `edge`
- `price`
- `expected_value`

This board highlights the highest-value current suggestions based on the platform’s current pricing logic.

### **4. Evaluation Board**
Primary source tables:
- `fact_bet_evaluation`
- `agg_clv_summary`
- `agg_suggestion_performance_summary`

Key fields:
- `matchup`
- `game_date`
- `bookmaker_title`
- `outcome_name`
- `clv_result`
- `bet_result`
- `suggested_price`
- `closing_price_proxy`

This page evaluates whether a suggestion held up against later observed prices and whether it won or lost once game results were available.

### **5. Research Board**
Primary source table:
- `agg_research_board`

Key fields:
- `game_date`
- `game_state`
- `market_shape_signal`
- `pricing_signal`
- `best_edge`
- `best_expected_value`

This board gives a structured summary of why a matchup looks interesting from a market standpoint.

---

## **How to Refresh the Dashboard Data**

Refreshing the Looker page only shows the most recent data already present in BigQuery.

To refresh the actual underlying data:
1. run the ingestion pipeline or Kestra flow
2. reload raw market tables into BigQuery
3. run `dbt run`
4. refresh Looker Studio

For a manual one-click refresh, use the Kestra market refresh flow.

---

## **Development Notes**

### **The Odds API Design Change**
The platform moved away from relying on simulated odds as the main source and now uses:
- `/events`
- `/odds`
- `/scores`

This was the key shift that made the dashboard useful for live and pre-game market analysis.

### **Bulk Odds Endpoint Can Return Empty**
One issue encountered was that the bulk odds endpoint sometimes returned no events even though the API request was technically valid. The loader was updated to fall back to:
- fetch current event IDs from `/events`
- then call `/events/{eventId}/odds`

This made odds ingestion much more reliable.

### **Kestra Environment Variables**
A major issue was that `THE_ODDS_API_KEY` was missing from `docker-compose.kestra.yml`, so flows worked locally but not from inside the Kestra container. The fix was to explicitly pass:
- `THE_ODDS_API_KEY`
- `THE_ODDS_SPORT`
- `THE_ODDS_REGIONS`
- `THE_ODDS_MARKETS`

into the Kestra service environment.

### **Kestra vs Local Postgres Host**
Another key issue was that:
- local scripts needed `POSTGRES_HOST=localhost`
- Kestra flows needed `POSTGRES_HOST=sportsbook_postgres`

This is because `localhost` inside a container points to the container itself, not the Postgres service.

### **Kestra Shell Behavior**
Kestra shell tasks use `sh`, not `bash`, so:
- `source .venv/bin/activate` failed
- direct `python3 -m ...` execution was more reliable

### **Google Credentials Inside Kestra**
BigQuery loads worked locally but initially failed inside Kestra because the container did not have Google ADC mounted. The fix was:
- mount `application_default_credentials.json`
- set `GOOGLE_APPLICATION_CREDENTIALS` in `docker-compose.kestra.yml`

### **dbt in Kestra Needed Its Own Profile**
The Kestra dbt task failed until a `profiles.yml` was created inside the container. The flow was updated to create `/root/.dbt/profiles.yml` before running `dbt run`.

### **Looker Field Type Issues**
Several Looker charts initially failed because numeric odds fields were interpreted incorrectly:
- odds fields were mis-typed as date-like fields
- some price fields were aggregated as Count Distinct instead of Min/Max/Number values

Fixing the data source field types and metric aggregations resolved the display issues.

### **BigQuery Load Method**
`load_table_from_dataframe()` introduced `pyarrow` dependency problems in the container. The project now uses:
- temporary CSV export
- `load_table_from_file()`

This was much more stable in both local and Kestra contexts.

### **dbt Project Path**
Another repeated issue was running dbt from the wrong folder. The correct path is always:

```bash
cd dbt/sportsbook_dbt
```

Running dbt elsewhere can build the wrong models or old boilerplate tables.

---

## **Current Scope**

### **Included in the current platform**
- real NBA event ingestion
- real bookmaker odds ingestion
- real score ingestion
- BigQuery raw market tables
- dbt market board and evaluation models
- manual Kestra refresh flow
- Looker Studio dashboard with live and pre-game views

### **Still intentionally limited**
- no fully finished AI reasoning layer yet
- no paid historical odds snapshots yet
- no automatic high-frequency refresh schedule yet
- no productionized closing-line logic beyond current proxy approach

### **Planned next improvements**
- improve suggestion logic beyond fixed edge assumptions
- tighten EV and vig modeling
- add better game-state freshness controls
- add automated refresh scheduling
- add historical odds snapshots if moving to a paid tier
