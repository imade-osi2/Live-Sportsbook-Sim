# **Live & Pre-Game Sports Betting Analytics Platform**

---

A production-style data engineering project that ingests real NBA events, bookmaker odds, and score data, transforms them into analytics-ready warehouse models, and publishes a live sportsbook-style reporting layer in Looker Studio.

The platform supports **two complementary pipeline paths**:

1. **Manual batch market refresh path**  
   Pulls the latest real NBA events, odds, and scores from APIs, loads them into PostgreSQL and BigQuery, rebuilds dbt models, and refreshes the dashboard.

2. **Kafka local streaming path**  
   Simulates live sportsbook-style event streams for bets, odds updates, and game updates using Kafka producers and consumers, then lands those events in PostgreSQL, BigQuery, and downstream dashboard models.

This lets the repo show both:
- a practical current-state market intelligence platform using real bookmaker data
- a more event-driven streaming architecture that can be automated further through Kestra later

---

## **Project Goal**

This project demonstrates a real-world sports data platform that combines:

- **real NBA event data**
- **real bookmaker odds**
- **real score / game-state data**
- **warehouse modeling for market analysis**
- **streaming event simulation with Kafka**
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

The platform combines API ingestion, local storage, streaming simulation, cloud warehousing, analytics engineering, orchestration, and BI delivery.

### **High-Level Flow**

#### **Path A — Manual Batch Market Refresh**
1. **The Odds API** provides real NBA events, odds, and scores
2. **Python ingestion jobs** load raw market data into PostgreSQL
3. **BigQuery loaders** move those raw tables into the analytics warehouse
4. **dbt** builds staging, mart, and aggregate models for reporting
5. **Kestra** can run the full manual refresh flow end to end
6. **Looker Studio** reads the curated models and displays live and pre-game market analytics

#### **Path B — Kafka Local Streaming Pipeline**
1. **Kafka producers** generate sportsbook-style event streams for bets, odds updates, and game updates
2. **Kafka consumers** read those messages and persist them into PostgreSQL raw stream tables
3. **BigQuery loaders** move stream tables into the analytics warehouse
4. **dbt** builds analytics models from the stream-backed warehouse tables
5. **Looker Studio** reads the resulting stream-informed dashboard tables

---

## **Architecture Components**

### **Market Data Sources**
- NBA event schedule and event IDs
- real bookmaker odds for moneyline, spreads, and totals
- live and completed score updates
- bookmaker-specific price snapshots across multiple books

### **Streaming Sources**
- simulated bet events
- simulated odds update events
- simulated game update events

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
- stream-backed betting activity and odds movement tables

### **Orchestration Layer**
Kestra is used to:
- manually refresh market data
- run end-to-end update flows
- automate warehouse refreshes later if desired
- serve as the future control point for a more automated streaming refresh path

### **Analytics Layer**
Looker Studio surfaces:
- overview KPIs
- live market board
- suggested bets board
- evaluation board
- research board
- historical stream-backed betting and odds movement views

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

The warehouse is centered around both real market data and stream-capable betting analytics.

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

### **Kafka / Stream-Oriented Models**
- `stg_bet_events`
- `stg_odds_updates`
- `stg_game_updates`
- `fact_bets`
- `fact_odds_history`
- `agg_betting_activity_by_game`
- `agg_market_type_summary`
- `agg_odds_movement_by_game`
- `agg_live_vs_pregame_bet_mix`

These stream-oriented models remain useful because they show how a live event-driven betting pipeline can be modeled, even while the current production-style dashboard is centered on real odds and score feeds.

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

## **Pipeline Path A — Manual Batch Market Refresh**

This is the current primary refresh path for the real market dashboard.

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

This path is ideal when:
- you want to conserve free-tier API calls
- you want a daily or manual refresh cycle
- you want the dashboard to reflect the most recent full warehouse state

---

## **Pipeline Path B — Kafka Local Streaming Pipeline**

This is the event-driven simulation path that shows how a live sportsbook stream can work.

### **1. Start Kafka consumers**
Run consumers first so they are ready to receive stream events:

```bash
python -m streaming.consumers.bets_consumer
python -m streaming.consumers.odds_consumer
python -m streaming.consumers.game_updates_consumer
```

### **2. Start Kafka producers**
Run producers to generate local sportsbook-style stream events:

```bash
python -m ingestion.producers.bets_producer
python -m ingestion.producers.odds_producer
python -m ingestion.producers.game_updates_producer
```

### **3. Load stream-backed raw tables into BigQuery**
```bash
python -m ingestion.batch_jobs.load_stream_tables_to_bigquery
```

### **4. Rebuild dbt stream models**
```bash
cd dbt/sportsbook_dbt
dbt run
```

This path is ideal when:
- you want to demonstrate streaming architecture knowledge
- you want to simulate live betting-style event flow
- you want to show how Kafka events can be landed, modeled, and visualized

### **What an automated streaming version would look like**
If you enable this path through Kestra later, the flow would look like:
1. trigger producer jobs on an interval
2. consume and store messages continuously
3. micro-batch or periodic-load stream tables into BigQuery
4. run dbt models on a short cadence
5. refresh the dashboard with near-real-time warehouse updates

That would turn the current local Kafka simulation into a more operational streaming refresh pattern.

---

## **Dashboard**

The dashboard is publicly accessible at:

🔗 **View Live Dashboard**  
https://datastudio.google.com/reporting/e96ea5f4-9ab8-47f7-b99f-5f9e9b22c042

The current dashboard presents a sportsbook-style operating view built around live and pre-game odds rather than raw ingestion tables.

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

### **6. Optional Stream Analytics Views**
If you want to expose more of the Kafka work in Looker Studio, you can add pages or charts from:
- `agg_betting_activity_by_game`
- `agg_market_type_summary`
- `agg_odds_movement_by_game`
- `agg_live_vs_pregame_bet_mix`

These show the event-driven side of the platform more explicitly.

---

## **Useful Betting Metrics in the Dashboard**

### **Latest H2H Price by Bookmaker**
Used to compare the current market price for each team across books.

Why it matters:
- helps identify the best available number
- shows whether a side is drifting or strengthening across books
- supports line-shopping logic

### **Best Expected Value**
Used on the research and suggested bets views.

Why it matters:
- summarizes the strongest current opportunity at the game level
- helps prioritize which games deserve manual review

### **Edge**
Represents the platform’s current difference between estimated fair probability and implied probability.

Why it matters:
- acts as a quick ranking measure for opportunity strength
- helps separate weak market noise from stronger signals

### **High-Confidence Suggestions**
Count of suggestions that passed the platform’s current higher-confidence thresholds.

Why it matters:
- prevents the dashboard from becoming just a giant list of all markets
- gives a smaller actionable subset

### **Beat Close Count / CLV Proxy**
Used on the evaluation page.

Why it matters:
- measures whether the platform found a better number than the later observed market price
- helps judge whether the process is finding timing advantages, not just random picks

### **Stream-Based Betting Activity**
Used by the Kafka path models.

Why it matters:
- shows how a live event flow could be summarized into handle, bet counts, market mix, and timing splits
- demonstrates warehouse modeling for event-driven sportsbook telemetry

---

## **How to Refresh the Dashboard Data**

Refreshing the Looker page only shows the most recent data already present in BigQuery.

### **For the real market dashboard**
1. run the manual batch ingestion pipeline or Kestra flow
2. reload raw market tables into BigQuery
3. run `dbt run`
4. refresh Looker Studio

### **For the Kafka event-driven dashboard path**
1. run consumers
2. run producers
3. load stream tables into BigQuery
4. run `dbt run`
5. refresh Looker Studio

For a manual one-click refresh of the real market path, use the Kestra market refresh flow.

---

## **Development Notes**

### **Dual-Pipeline Design**
The repo now intentionally keeps both paths:
- a real market batch path using The Odds API
- a Kafka local streaming path for simulated live event flow

This is useful because it shows both:
- practical market analytics engineering
- event-driven streaming architecture

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

## **Troubleshooting**

### **If odds rows load as 0**
Check:
- whether the bulk `/odds` endpoint is currently empty
- whether the event-level odds fallback is working
- whether `THE_ODDS_API_KEY` exists in the Kestra container env

### **If Kestra can’t talk to Postgres**
Check:
- `POSTGRES_HOST=sportsbook_postgres` in Kestra
- that all containers share the same Docker network
- that the container password matches the real Postgres password

### **If dbt fails inside Kestra**
Check:
- `/root/.dbt/profiles.yml` exists
- Google ADC is mounted
- the dbt task is running from `/workspace/dbt/sportsbook_dbt`

### **If Looker does not show a table**
Check:
- the model exists in BigQuery
- the data source has been refreshed
- numeric odds fields are not using Count Distinct aggregation
- you are using the curated aggregate models, not raw tables

### **If local stream loads fail**
Check:
- Kafka consumers are running before producers
- `POSTGRES_HOST=localhost` is used for local terminal execution
- stream raw tables in PostgreSQL actually contain rows before BigQuery load
- `dbt run` is rerun after stream tables are refreshed

---

## **Current Scope**

### **Included in the current platform**
- real NBA event ingestion
- real bookmaker odds ingestion
- real score ingestion
- BigQuery raw market tables
- dbt market board and evaluation models
- manual Kestra refresh flow
- Kafka local streaming pipeline for sportsbook-style events
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
- automate the real market refresh cadence
- optionally automate the Kafka streaming refresh path through Kestra
- add historical odds snapshots if moving to a paid tier
