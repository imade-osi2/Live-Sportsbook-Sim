import os
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()


PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET = os.getenv("BIGQUERY_DATASET")


def fetch_table(query: str) -> pd.DataFrame:
    conn = get_postgres_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_dataframe(df: pd.DataFrame, table_name: str) -> None:
    table_id = f"{PROJECT_ID}.{DATASET}.{table_name}"
    client = bigquery.Client(project=PROJECT_ID)
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
    print(f"Loaded {len(df)} rows to {table_id}")


def main():
    bets_df = fetch_table("""
        SELECT bet_id, user_id, game_id, market_type, selection, stake, odds, bet_time, ingested_at
        FROM raw.bet_events_stream
        ORDER BY bet_id
    """)
    load_dataframe(bets_df, "raw_bet_events_stream")

    odds_df = fetch_table("""
        SELECT odds_event_id, game_id, sportsbook, market_type, home_odds, away_odds, spread, total_points, event_time, ingested_at
        FROM raw.odds_updates_stream
        ORDER BY odds_event_id
    """)
    load_dataframe(odds_df, "raw_odds_updates_stream")

    game_df = fetch_table("""
        SELECT game_event_id, game_id, game_status, home_score, away_score, event_time, ingested_at
        FROM raw.game_updates_stream
        ORDER BY game_event_id
    """)
    load_dataframe(game_df, "raw_game_updates_stream")


if __name__ == "__main__":
    main()