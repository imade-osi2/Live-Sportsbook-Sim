import os
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from ingestion.api_clients.postgres_client import get_postgres_connection

load_dotenv()


def fetch_games():
    conn = get_postgres_connection()
    query = """
        SELECT
            game_id,
            game_date,
            season,
            home_team,
            away_team,
            game_status,
            home_score,
            away_score,
            created_at
        FROM raw.nba_games
        ORDER BY game_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def load_to_bigquery(df):
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset = os.getenv("BIGQUERY_DATASET")
    table_id = f"{project_id}.{dataset}.raw_nba_games"

    client = bigquery.Client(project=project_id)

    job = client.load_table_from_dataframe(df, table_id)
    job.result()

    print(f"Loaded {len(df)} rows to {table_id}")


if __name__ == "__main__":
    df = fetch_games()
    load_to_bigquery(df)