import os
import requests
from dotenv import load_dotenv
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")
SPORT = os.getenv("THE_ODDS_SPORT", "basketball_nba")
REGIONS = os.getenv("THE_ODDS_REGIONS", "us")
MARKETS = os.getenv("THE_ODDS_MARKETS", "h2h,spreads,totals")

BASE_URL = "https://api.the-odds-api.com/v4"
BULK_ODDS_URL = f"{BASE_URL}/sports/{SPORT}/odds"
EVENTS_URL = f"{BASE_URL}/sports/{SPORT}/events"


def request_json(url: str, params: dict) -> list | dict:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    remaining = response.headers.get("x-requests-remaining")
    used = response.headers.get("x-requests-used")
    last_cost = response.headers.get("x-requests-last")

    print(
        f"Request ok | remaining={remaining} used={used} last_cost={last_cost} url={response.url}"
    )

    return response.json()


def fetch_bulk_odds() -> list:
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    data = request_json(BULK_ODDS_URL, params)
    return data if isinstance(data, list) else []


def fetch_events() -> list:
    params = {
        "apiKey": API_KEY,
        "dateFormat": "iso",
    }
    data = request_json(EVENTS_URL, params)
    return data if isinstance(data, list) else []


def fetch_event_odds(event_id: str) -> dict:
    url = f"{BASE_URL}/sports/{SPORT}/events/{event_id}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    data = request_json(url, params)
    return data if isinstance(data, dict) else {}


def get_odds_events() -> list:
    bulk_events = fetch_bulk_odds()

    if bulk_events:
        print(f"Bulk odds returned {len(bulk_events)} events.")
        return bulk_events

    print("Bulk odds returned 0 events. Falling back to /events + /events/{eventId}/odds ...")

    events = fetch_events()
    if not events:
        print("No NBA events returned from /events either.")
        return []

    odds_events = []
    for event in events:
        event_id = event.get("id")
        if not event_id:
            continue

        event_odds = fetch_event_odds(event_id)
        if event_odds and event_odds.get("bookmakers"):
            odds_events.append(event_odds)

    print(f"Per-event odds returned {len(odds_events)} events with bookmakers.")
    return odds_events


def load_odds_to_postgres(events: list) -> None:
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.nba_odds_api (
            odds_record_id,
            event_id,
            sport_key,
            commence_time,
            home_team,
            away_team,
            bookmaker_key,
            bookmaker_title,
            market_key,
            outcome_name,
            price,
            point,
            last_update
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (odds_record_id) DO NOTHING
    """

    rows_loaded = 0

    for event in events:
        event_id = event.get("id")
        sport_key = event.get("sport_key")
        commence_time = event.get("commence_time")
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        for bookmaker in event.get("bookmakers", []):
            bookmaker_key = bookmaker.get("key")
            bookmaker_title = bookmaker.get("title")

            for market in bookmaker.get("markets", []):
                market_key = market.get("key")
                last_update = market.get("last_update")

                for outcome in market.get("outcomes", []):
                    outcome_name = outcome.get("name")
                    price = outcome.get("price")
                    point = outcome.get("point")

                    odds_record_id = (
                        f"{event_id}_{bookmaker_key}_{market_key}_{outcome_name}_{last_update}"
                    )

                    cur.execute(
                        insert_sql,
                        (
                            odds_record_id,
                            event_id,
                            sport_key,
                            commence_time,
                            home_team,
                            away_team,
                            bookmaker_key,
                            bookmaker_title,
                            market_key,
                            outcome_name,
                            price,
                            point,
                            last_update,
                        ),
                    )
                    rows_loaded += 1

    conn.commit()
    cur.close()
    conn.close()

    print(f"Loaded {rows_loaded} odds rows into Postgres.")


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("Missing THE_ODDS_API_KEY in .env")

    odds_events = get_odds_events()
    load_odds_to_postgres(odds_events)