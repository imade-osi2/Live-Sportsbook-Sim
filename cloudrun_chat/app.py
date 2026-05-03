from flask import Flask, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)
client = bigquery.Client()

DATASET = "de26-live-sportsbook-sim.de26_sportsbook_analytics"

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/query")
def query():
    body = request.get_json(force=True)
    prompt = body.get("prompt", "").lower()

    if "edge tonight" in prompt or "games with edge" in prompt:
        sql = f"""
        SELECT
          game_date,
          matchup,
          game_state,
          bookmaker_title,
          outcome_name,
          edge,
          expected_value,
          confidence_tier
        FROM `{DATASET}.agg_suggested_bets_board`
        WHERE edge >= 0.03
        ORDER BY expected_value DESC
        LIMIT 10
        """
    elif "best price" in prompt:
        sql = f"""
        SELECT
          game_date,
          matchup,
          market_key,
          outcome_name,
          best_bookmaker,
          best_price,
          worst_bookmaker,
          worst_price,
          price_gap
        FROM `{DATASET}.agg_best_price_by_outcome`
        ORDER BY price_gap DESC
        LIMIT 10
        """
    elif "live games" in prompt:
        sql = f"""
        SELECT
          game_date,
          matchup,
          game_state,
          bookmaker_title,
          outcome_name,
          latest_h2h_price,
          home_score,
          away_score
        FROM `{DATASET}.agg_live_game_metrics`
        ORDER BY odds_last_update DESC
        LIMIT 10
        """
    else:
        return jsonify({"error": "Prompt not supported yet."}), 400

    rows = [dict(r) for r in client.query(sql).result()]
    return jsonify({"rows": rows})