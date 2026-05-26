import datetime as dt
import decimal
import os

from flask import Flask, jsonify, render_template, request
from google.cloud import bigquery


app = Flask(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "de26-live-sportsbook-sim")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "de26_sportsbook_analytics")
BQ_LOCATION = os.getenv("BIGQUERY_LOCATION", "US")
DATASET = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}"


def get_result_limit():
    raw_limit = os.getenv("CHAT_RESULT_LIMIT", "10")
    try:
        return max(1, min(int(raw_limit), 50))
    except ValueError:
        return 10


RESULT_LIMIT = get_result_limit()

_client = None


def get_client():
    global _client
    if _client is None:
        _client = bigquery.Client(project=GCP_PROJECT_ID)
    return _client


def normalize_value(value):
    if isinstance(value, (dt.date, dt.datetime, dt.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value


def rows_to_dicts(rows):
    return [
        {key: normalize_value(value) for key, value in dict(row).items()}
        for row in rows
    ]


def run_query(sql):
    return rows_to_dicts(get_client().query(sql, location=BQ_LOCATION).result())


def choose_intent(prompt):
    text = prompt.lower()

    if any(term in text for term in ["kpi", "summary", "overview", "platform"]):
        return "platform_kpis"
    if any(term in text for term in ["clv", "closing", "beat close", "beat-close"]):
        return "clv_summary"
    if any(term in text for term in ["bookmaker", "book", "opportunities"]):
        return "bookmaker_opportunities"
    if any(term in text for term in ["edge", "value", "suggested", "recommendation"]):
        return "edge_opportunities"
    if any(term in text for term in ["live", "score", "scores", "game stats", "stats"]):
        return "live_games"
    if any(term in text for term in ["pregame", "odds", "line", "price", "best number"]):
        return "best_prices"
    return None


QUERY_TEMPLATES = {
    "platform_kpis": {
        "title": "Platform KPIs",
        "empty": "No KPI rows are available yet. Run the ingestion and dbt refresh after the Odds API quota resets.",
        "summary": "Here is the current platform summary from the curated KPI mart.",
        "sql": f"""
            SELECT
              active_games,
              bookmakers_tracked,
              total_suggestions,
              high_confidence_suggestions,
              avg_expected_value,
              avg_edge,
              beat_close_pct
            FROM `{DATASET}.agg_platform_kpis`
            LIMIT 1
        """,
    },
    "best_prices": {
        "title": "Best Numbers Across Books",
        "empty": "No current best-price rows were found. This usually means the Odds API refresh has not run with fresh current-slate data.",
        "summary": "These are the largest current price gaps across books.",
        "sql": f"""
            SELECT
              game_date,
              matchup,
              slate_bucket,
              market_key,
              outcome_name,
              best_bookmaker,
              best_price,
              worst_bookmaker,
              worst_price,
              price_gap,
              implied_prob_gap_pp
            FROM `{DATASET}.agg_best_price_by_outcome`
            ORDER BY implied_prob_gap_pp DESC, price_gap DESC
            LIMIT {RESULT_LIMIT}
        """,
    },
    "edge_opportunities": {
        "title": "Suggested Edge Opportunities",
        "empty": "No current edge suggestions were found. Current-slate suggestion marts may be empty until fresh odds data lands.",
        "summary": "These are the strongest current suggested bets by expected value.",
        "sql": f"""
            SELECT
              game_date,
              matchup,
              game_state,
              bookmaker_title,
              market_key,
              outcome_name,
              price,
              edge,
              expected_value,
              confidence_tier,
              rationale
            FROM `{DATASET}.agg_suggested_bets_board`
            ORDER BY expected_value DESC, edge DESC
            LIMIT {RESULT_LIMIT}
        """,
    },
    "live_games": {
        "title": "Live Game Metrics",
        "empty": "No live game rows were found. Live metrics depend on fresh score and odds refreshes.",
        "summary": "These are the latest live or final game metrics available.",
        "sql": f"""
            SELECT
              game_date,
              matchup,
              game_state,
              bookmaker_title,
              outcome_name,
              latest_h2h_price,
              home_score,
              away_score,
              odds_last_update
            FROM `{DATASET}.agg_live_game_metrics`
            ORDER BY odds_last_update DESC
            LIMIT {RESULT_LIMIT}
        """,
    },
    "bookmaker_opportunities": {
        "title": "Bookmaker Edge Opportunities",
        "empty": "No bookmaker opportunity rows were found for the current slate.",
        "summary": "These books currently show the most medium/high confidence opportunities.",
        "sql": f"""
            SELECT
              bookmaker_title,
              opportunity_count,
              avg_expected_value,
              avg_edge
            FROM `{DATASET}.agg_bookmaker_edge_opportunities`
            ORDER BY opportunity_count DESC, avg_expected_value DESC
            LIMIT {RESULT_LIMIT}
        """,
    },
    "clv_summary": {
        "title": "Closing Line Value Summary",
        "empty": "No CLV rows are available yet. CLV fills in after suggestions can be compared with later observed prices.",
        "summary": "Here is the current beat-close and expected value summary by signal tier and market.",
        "sql": f"""
            SELECT
              confidence_tier,
              market_key,
              evaluated_suggestions,
              beat_close_count,
              push_close_count,
              lost_close_count,
              beat_close_pct,
              avg_edge,
              avg_expected_value
            FROM `{DATASET}.agg_clv_summary`
            ORDER BY beat_close_pct DESC, evaluated_suggestions DESC
            LIMIT {RESULT_LIMIT}
        """,
    },
}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "dataset": DATASET,
            "location": BQ_LOCATION,
        }
    )


@app.post("/query")
def query():
    if not request.is_json:
        return jsonify({"error": "Request body must be a JSON object."}), 400

    parsed_body = request.get_json(silent=True)
    body = parsed_body if parsed_body is not None else {}
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    prompt_value = body.get("prompt", "")
    if not isinstance(prompt_value, str):
        return jsonify({"error": "Prompt must be a string."}), 400

    prompt = prompt_value.strip()

    if not prompt:
        return jsonify({"error": "Enter a question to search the sportsbook data."}), 400

    intent = choose_intent(prompt)
    if intent is None:
        return jsonify(
            {
                "error": "I can answer questions about best prices, live games, edge, CLV, bookmaker opportunities, and KPIs.",
                "supported_intents": list(QUERY_TEMPLATES.keys()),
            }
        ), 400

    template = QUERY_TEMPLATES[intent]
    try:
        rows = run_query(template["sql"])
    except Exception:
        app.logger.exception("BigQuery chat query failed for intent=%s", intent)
        return jsonify(
            {
                "error": "The chat route matched your question, but BigQuery could not return results. Check Cloud Run service account permissions, dataset config, and whether dbt has built the mart.",
                "intent": intent,
                "title": template["title"],
            }
        ), 502

    return jsonify(
        {
            "intent": intent,
            "title": template["title"],
            "answer": template["summary"] if rows else template["empty"],
            "row_count": len(rows),
            "rows": rows,
        }
    )
