# Live & Pre-Game Sports Betting Market Intelligence Platform

A production-style data engineering capstone that pulls NBA market data from APIs, processes it through a reproducible warehouse pipeline, and delivers a dashboard for **live market monitoring, pregame price comparison, bookmaker edge discovery, and bet evaluation**.

---

## Problem This Capstone Solves

Sports betting markets move quickly, but raw odds feeds alone do not make it easy to answer practical questions such as:

- Which books currently have the **best number**?
- Where are the **largest price gaps** across books?
- Which games are **live vs pregame** right now?
- Which suggested bets appear to have the strongest **edge / expected value**?
- Are suggested bets actually **beating the closing line**?

The capstone solves this by turning raw API data into a structured analytics system that supports market intelligence, line shopping, and evaluation.

---

## Solution Overview

This project builds an end-to-end data platform that:

1. Pulls **pregame odds, live odds, scores, and game-state data** from The Odds API.
2. Lands raw data into a **codified raw layer**.
3. Loads curated raw tables into **BigQuery**.
4. Uses **dbt** to build staged, fact, and aggregate models.
5. Serves a polished **Looker Studio dashboard** for live and pregame market monitoring.
6. Uses **two Kestra flows**:
   - a **manual pregame refresh flow**
   - a **live refresh flow** for in-game updates

---

## Final Dashboard Target

The dashboard is designed to look like the reference below and will remain organized into fixed sections so the reporting experience stays clean and repeatable.

![Final Dashboard Reference](./docs/images/final_dashboard_reference.png)

### Dashboard Layout

**Row 1 — KPI Scorecards**
- Active Games
- Bookmakers Tracked
- Best Price Gaps
- High-Confidence Signals
- Beat Close %
- Avg Expected Value

**Row 2 — Market Overview Charts**
- Live vs Pre-Game Market Mix
- Best Price Gap by Market
- Bookmaker Edge Opportunities

**Row 3 — Best Numbers Across Books**
- Table showing matchup, game state, market, outcome, best/worst bookmaker, best/worst price, and price gap

**Row 4 — Performance / Signal Monitoring**
- Closing Line Value Trend (CLV %)
- Signals by Confidence Tier

**Row 5 — Suggestion + Evaluation Tables**
- Top Suggested Bets
- Evaluation Snapshot

**Row 6 — Live Game Metrics Table**
- Latest live metrics available from the API, such as game state, latest prices, live score context, and other in-game fields surfaced by the live refresh flow

---

## End-to-End Data Engineering Flow

The platform follows the architecture shown below.

![Data Pipeline Overview](./docs/images/data_pipeline_overview.png)

---

## Core Data Flow

### 1. API Pull Layer
Data is pulled from **The Odds API** for:
- events / matchups
- pregame odds
- live odds
- scores / game state

### 2. Raw Ingestion Layer
Raw API payloads are landed into a **PostgreSQL raw layer** using **codified schemas**.

Example raw tables:
- `raw.nba_events_api`
- `raw.nba_odds_api`
- `raw.nba_scores_api`
- raw stream tables (optional Kafka path)

### 3. Warehouse Layer
Raw data is loaded into **BigQuery**, where the warehouse is organized into:
- **raw layer**
- **staging layer**
- **mart / aggregate layer**

### 4. Transformation Layer
**dbt** transforms the data into business-ready tables.

Example core models:
- `fact_real_odds_history`
- `fact_real_scores`
- `agg_best_price_by_outcome`
- `agg_clv_kpis`
- `agg_suggested_bets_board`
- `agg_live_market_board`
- `fact_bet_evaluation`

### 5. Dashboard Layer
**Looker Studio** reads from the aggregate / mart tables and presents a clear monitoring interface.

---

## Two Kestra Refresh Paths

### 1. Manual Pregame Refresh Flow
Used for controlled refreshes of pregame market data.

High-level flow:
1. Pull latest pregame markets
2. Load raw / warehouse tables
3. Run dbt marts
4. Refresh dashboard data

### 2. Live Refresh Flow
Used during active games to keep live data current.

High-level flow:
1. Poll live odds and scores on an interval
2. Update live raw tables
3. Run targeted dbt models
4. Refresh dashboard data

This split keeps the project practical and cost-aware while still supporting a near-live dashboard experience.

---

## Partitioning and Clustering

A key improvement from earlier feedback is making warehouse tables more production-like by explicitly using **partitioning** and **clustering** where appropriate.

### Why it matters
- improves query performance
- reduces BigQuery scan cost
- makes dashboards faster
- makes the warehouse design more realistic

### Target approach
Typical mart / fact tables should be:
- **partitioned by date**, such as `game_date`, `snapshot_date`, or `loaded_at`
- **clustered by frequently filtered fields**, such as:
  - `event_id`
  - `bookmaker_title`
  - `market_key`
  - `game_state`

This should be declared in dbt configs so the physical design is reproducible and not just implied.

---

## Codified Schema and Reproducibility

Another major improvement is ensuring the raw layer and pipeline setup are reproducible.

### What this means
- raw table structure is defined in code
- schema expectations are documented and version-controlled
- environment variables are explicit
- credentials and setup steps are clearly documented
- warehouse design is consistent across runs

### Reproducibility goals
- another developer can clone the repo and understand the pipeline layout quickly
- raw ingestion fields are not “hidden” in ad hoc code only
- setup issues around credentials, dbt profiles, and container networking are easier to avoid

---

## Planned Outcome for the Capstone

By the end of this capstone, the project should demonstrate:

- a realistic API-to-warehouse pipeline
- structured raw, staging, and mart layers
- production-style orchestration with **Kestra**
- partitioned and clustered warehouse tables
- codified schema / improved reproducibility
- a polished **Looker Studio dashboard** focused on sportsbook market intelligence
- both **manual pregame** and **live refresh** operating paths

---

## Why This Project Is Valuable

This project is useful because it shows more than just dashboarding. It demonstrates the full data engineering workflow:

- API ingestion
- raw data handling
- warehouse modeling
- dbt transformations
- orchestration
- analytics delivery
- market intelligence use cases

It also ties the data work to a practical business question:

> How do we turn raw sportsbook market data into usable insight that helps identify better prices, monitor live markets, and evaluate whether suggested bets are truly showing edge?

---

## Current Scope

### Included now
- NBA events
- pregame odds
- live odds support path
- scores / game state
- BigQuery warehouse models
- Looker Studio dashboard
- manual pregame + live Kestra refresh design

### Future extensions
- stronger bet suggestion / evaluation logic
- richer CLV analysis
- additional sports
- more advanced live game metrics
- optional Kafka-enabled streaming demo path

---

## Notes for Repo Users

If you reuse this project, keep these points in mind:

- Looker Studio does **not** auto-refresh continuously, so page refresh is required after new data loads.
- Live updates are handled through the **live Kestra flow**, not by Looker itself.
- dbt transformations run **in BigQuery**; dbt compiles SQL locally but executes the transformations in the warehouse.
- The warehouse table design should stay aligned with dashboard needs so charts remain easy to maintain.
- Partitioning, clustering, and codified schemas are not optional polish — they are important parts of making the capstone more production-like.

---

## Project Status

This README reflects the **updated dashboard plan** and the intended end-state for the capstone. It is meant to guide the next implementation steps while clearly communicating the problem, architecture, and final analytics experience.
