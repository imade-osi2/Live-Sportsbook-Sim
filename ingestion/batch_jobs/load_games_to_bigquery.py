import os
import tempfile
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


if __name__ == "__main__":
    df = fetch_games()
    load_to_bigquery(df)