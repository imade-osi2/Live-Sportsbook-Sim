import datetime as dt
import decimal
import os
from concurrent.futures import TimeoutError

from flask import Flask, jsonify, render_template, request
from google.cloud import bigquery


app = Flask(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "de26-live-sportsbook-sim")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "de26_sportsbook_analytics")
BQ_LOCATION = os.getenv("BIGQUERY_LOCATION", "US")
DATASET = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}"


def get_int_env(name, default, minimum, maximum):
    raw_value = os.getenv(name, str(default))
    try:
        return max(minimum, min(int(raw_value), maximum))
    except ValueError:
        return default


def get_result_limit():
    return get_int_env("CHAT_RESULT_LIMIT", 10, 1, 50)


RESULT_LIMIT = get_result_limit()
MAX_PROMPT_CHARS = get_int_env("CHAT_MAX_PROMPT_CHARS", 500, 50, 2000)
QUERY_TIMEOUT_SECONDS = get_int_env("CHAT_QUERY_TIMEOUT_SECONDS", 20, 5, 120)

_client = None


class QueryTimeoutError(Exception):
    pass


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
    job = get_client().query(sql, location=BQ_LOCATION)
    try:
        return rows_to_dicts(job.result(timeout=QUERY_TIMEOUT_SECONDS))
    except TimeoutError as exc:
        job.cancel()
        raise QueryTimeoutError from exc


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
        "label": "Platform KPIs",
        "prompt": "Show platform KPIs",
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
        "label": "Best prices",
        "prompt": "Show me the best prices across books",
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
        "label": "Games with edge",
        "prompt": "Which games have edge right now?",
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
        "label": "Live games",
        "prompt": "Show live games and scores",
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
        "label": "Bookmaker gaps",
        "prompt": "Which bookmakers have the most opportunities?",
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
        "label": "CLV summary",
        "prompt": "Give me CLV summary",
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


def serialize_intents():
    return [
        {
            "id": intent_id,
            "title": template["title"],
            "label": template["label"],
            "prompt": template["prompt"],
        }
        for intent_id, template in QUERY_TEMPLATES.items()
    ]


@app.get("/")
def index():
    return render_template(
        "index.html",
        intents=serialize_intents(),
        max_prompt_chars=MAX_PROMPT_CHARS,
    )


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "dataset": DATASET,
            "location": BQ_LOCATION,
            "max_prompt_chars": MAX_PROMPT_CHARS,
            "query_timeout_seconds": QUERY_TIMEOUT_SECONDS,
            "result_limit": RESULT_LIMIT,
        }
    )


@app.get("/intents")
def intents():
    return jsonify({"intents": serialize_intents()})


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
    intent_value = body.get("intent", "")
    if not isinstance(intent_value, str):
        return jsonify({"error": "Intent must be a string."}), 400

    prompt = prompt_value.strip()
    requested_intent = intent_value.strip()

    if not prompt:
        return jsonify({"error": "Enter a question to search the sportsbook data."}), 400
    if len(prompt) > MAX_PROMPT_CHARS:
        return jsonify(
            {
                "error": f"Prompt is too long. Keep questions under {MAX_PROMPT_CHARS} characters.",
            }
        ), 400

    intent = requested_intent or choose_intent(prompt)
    if intent is None:
        return jsonify(
            {
                "error": "I can answer questions about best prices, live games, edge, CLV, bookmaker opportunities, and KPIs.",
                "supported_intents": list(QUERY_TEMPLATES.keys()),
            }
        ), 400
    if intent not in QUERY_TEMPLATES:
        return jsonify(
            {
                "error": "Intent is not supported by this chat service.",
                "supported_intents": list(QUERY_TEMPLATES.keys()),
            }
        ), 400

    template = QUERY_TEMPLATES[intent]
    try:
        rows = run_query(template["sql"])
    except QueryTimeoutError:
        app.logger.warning("BigQuery chat query timed out for intent=%s", intent)
        return jsonify(
            {
                "error": "The BigQuery request timed out. Try a narrower question or retry shortly.",
                "intent": intent,
                "title": template["title"],
            }
        ), 504
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
