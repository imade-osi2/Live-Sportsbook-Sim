import json
from kafka import KafkaConsumer
from ingestion.api_clients.postgres_client import get_postgres_connection

consumer = KafkaConsumer(
    "odds_updates",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="odds-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

def insert_odds_event(event):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.odds_updates_stream (
            odds_event_id,
            game_id,
            sportsbook,
            market_type,
            home_odds,
            away_odds,
            spread,
            total_points,
            event_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (odds_event_id) DO NOTHING
    """

    cur.execute(
        insert_sql,
        (
            event["odds_event_id"],
            event["game_id"],
            event["sportsbook"],
            event["market_type"],
            event["home_odds"],
            event["away_odds"],
            event["spread"],
            event["total_points"],
            event["event_time"],
        ),
    )

    conn.commit()
    cur.close()
    conn.close()

print("Listening for odds updates...")

for message in consumer:
    event = message.value
    insert_odds_event(event)
    print(f"Inserted odds event: {event}")