import os
import tempfile
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

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        temp_path = tmp_file.name

    with open(temp_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    job.result()
    os.remove(temp_path)
    print(f"Loaded {len(df)} rows to {table_id}")


def main():
    events_df = fetch_table("""
        SELECT event_id, sport_key, sport_title, commence_time, home_team, away_team, created_at
        FROM raw.nba_events_api
    """)
    load_dataframe(events_df, "raw_nba_events_api")

    odds_df = fetch_table("""
        SELECT odds_record_id, event_id, sport_key, commence_time, home_team, away_team,
               bookmaker_key, bookmaker_title, market_key, outcome_name, price, point,
               last_update, created_at
        FROM raw.nba_odds_api
    """)
    load_dataframe(odds_df, "raw_nba_odds_api")

    scores_df = fetch_table("""
        SELECT score_record_id, event_id, sport_key, sport_title, commence_time, completed,
               home_team, away_team, home_score, away_score, last_update, created_at
        FROM raw.nba_scores_api
    """)
    load_dataframe(scores_df, "raw_nba_scores_api")


if __name__ == "__main__":
    main()