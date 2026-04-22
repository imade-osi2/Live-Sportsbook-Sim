import os
import requests
from dotenv import load_dotenv
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()

API_KEY = os.getenv("THE_ODDS_API_KEY")
SPORT = os.getenv("THE_ODDS_SPORT", "basketball_nba")
REGIONS = os.getenv("THE_ODDS_REGIONS", "us")
MARKETS = os.getenv("THE_ODDS_MARKETS", "h2h,spreads,totals")
API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"


def fetch_odds():
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def load_odds_to_postgres(events):
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
        event_id = event["id"]
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