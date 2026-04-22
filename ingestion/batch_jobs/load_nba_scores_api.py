import os
import requests
from dotenv import load_dotenv
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")
SPORT = os.getenv("THE_ODDS_SPORT", "basketball_nba")
API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/scores"


def fetch_scores(days_from: int | None = None):
    params = {
        "apiKey": API_KEY,
        "dateFormat": "iso",
    }
    if days_from is not None:
        params["daysFrom"] = days_from

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def extract_team_score(scores, team_name):
    if not scores:
        return None
    for item in scores:
        if item.get("name") == team_name:
            score = item.get("score")
            return int(score) if score is not None else None
    return None


def load_scores_to_postgres(events):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.nba_scores_api (
            score_record_id,
            event_id,
            sport_key,
            sport_title,
            commence_time,
            completed,
            home_team,
            away_team,
            home_score,
            away_score,
            last_update
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (score_record_id) DO UPDATE SET
            completed = EXCLUDED.completed,
            home_score = EXCLUDED.home_score,
            away_score = EXCLUDED.away_score,
            last_update = EXCLUDED.last_update
    """

    rows_loaded = 0

    for event in events:
        event_id = event["id"]
        sport_key = event.get("sport_key")
        sport_title = event.get("sport_title")
        commence_time = event.get("commence_time")
        completed = event.get("completed")
        home_team = event.get("home_team")
        away_team = event.get("away_team")
        scores = event.get("scores")
        last_update = event.get("last_update")

        home_score = extract_team_score(scores, home_team)
        away_score = extract_team_score(scores, away_team)

        score_record_id = f"{event_id}_{last_update or 'no_update'}"

        cur.execute(
            insert_sql,
            (
                score_record_id,
                event_id,
                sport_key,
                sport_title,
                commence_time,
                completed,
                home_team,
                away_team,
                home_score,
                away_score,
                last_update,
            ),
        )
        rows_loaded += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {rows_loaded} score rows into Postgres.")


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("Missing THE_ODDS_API_KEY in .env")

    events = fetch_scores(days_from=1)
    load_scores_to_postgres(events)