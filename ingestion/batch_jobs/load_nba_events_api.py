import os
import requests
from dotenv import load_dotenv
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")
SPORT = os.getenv("THE_ODDS_SPORT", "basketball_nba")
API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/events"


def fetch_events():
    params = {
        "apiKey": API_KEY,
        "dateFormat": "iso",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def load_events_to_postgres(events):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.nba_events_api (
            event_id,
            sport_key,
            sport_title,
            commence_time,
            home_team,
            away_team
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (event_id) DO UPDATE SET
            sport_key = EXCLUDED.sport_key,
            sport_title = EXCLUDED.sport_title,
            commence_time = EXCLUDED.commence_time,
            home_team = EXCLUDED.home_team,
            away_team = EXCLUDED.away_team
    """

    for event in events:
        cur.execute(
            insert_sql,
            (
                event["id"],
                event.get("sport_key"),
                event.get("sport_title"),
                event.get("commence_time"),
                event.get("home_team"),
                event.get("away_team"),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(events)} event rows into Postgres.")


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("Missing THE_ODDS_API_KEY in .env")

    events = fetch_events()
    load_events_to_postgres(events)