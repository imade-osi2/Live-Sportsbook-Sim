import os
import requests
from dotenv import load_dotenv
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()

API_URL = "https://api.balldontlie.io/v1/games"
API_KEY = os.getenv("BALLDONTLIE_API_KEY")


def fetch_games(season: int = 2025, per_page: int = 25):
    headers = {
        "Authorization": API_KEY
    }

    params = {
        "seasons[]": season,
        "per_page": per_page,
    }

    response = requests.get(API_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json().get("data", [])
    return data


def map_game_status(status: str) -> str:
    if status == "Final":
        return "final"
    if "Q" in status or "Halftime" in status:
        return "in_progress"
    return "scheduled"


def load_games_to_postgres(games):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.nba_games (
            game_id,
            game_date,
            season,
            home_team,
            away_team,
            game_status,
            home_score,
            away_score
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (game_id) DO UPDATE SET
            game_date = EXCLUDED.game_date,
            season = EXCLUDED.season,
            home_team = EXCLUDED.home_team,
            away_team = EXCLUDED.away_team,
            game_status = EXCLUDED.game_status,
            home_score = EXCLUDED.home_score,
            away_score = EXCLUDED.away_score
    """

    for game in games:
        game_id = f"nba_{game['id']}"
        game_date = game["date"][:10]
        season = str(game["season"])
        home_team = game["home_team"]["full_name"]
        away_team = game["visitor_team"]["full_name"]
        game_status = map_game_status(game["status"])
        home_score = game["home_team_score"]
        away_score = game["visitor_team_score"]

        cur.execute(
            insert_sql,
            (
                game_id,
                game_date,
                season,
                home_team,
                away_team,
                game_status,
                home_score,
                away_score,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Loaded {len(games)} NBA games into Postgres.")


if __name__ == "__main__":
    if not API_KEY:
        raise ValueError("Missing BALLDONTLIE_API_KEY in your .env file.")

    games = fetch_games(season=2025, per_page=25)
    load_games_to_postgres(games)