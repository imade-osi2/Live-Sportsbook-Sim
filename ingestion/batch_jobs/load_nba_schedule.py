from ingestion.api_clients.postgres_client import get_postgres_connection


sample_games = [
    {
        "game_id": "nba_002",
        "game_date": "2026-04-17",
        "season": "2025-2026",
        "home_team": "Hornets",
        "away_team": "Magic",
        "game_status": "scheduled",
        "home_score": 0,
        "away_score": 0,
    },
    {
        "game_id": "nba_003",
        "game_date": "2026-04-17",
        "season": "2025-2026",
        "home_team": "Warriors",
        "away_team": "Suns",
        "game_status": "scheduled",
        "home_score": 0,
        "away_score": 0,
    },
]


def load_games():
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
        ON CONFLICT (game_id) DO NOTHING
    """

    for game in sample_games:
        cur.execute(
            insert_sql,
            (
                game["game_id"],
                game["game_date"],
                game["season"],
                game["home_team"],
                game["away_team"],
                game["game_status"],
                game["home_score"],
                game["away_score"],
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("NBA schedule load complete.")


if __name__ == "__main__":
    load_games()