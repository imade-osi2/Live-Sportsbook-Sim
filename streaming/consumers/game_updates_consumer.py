import json
from kafka import KafkaConsumer
from ingestion.api_clients.postgres_client import get_postgres_connection

consumer = KafkaConsumer(
    "game_updates",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="game-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

def insert_game_event(event):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.game_updates_stream (
            game_event_id,
            game_id,
            game_status,
            home_score,
            away_score,
            event_time
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (game_event_id) DO NOTHING
    """

    cur.execute(
        insert_sql,
        (
            event["game_event_id"],
            event["game_id"],
            event["game_status"],
            event["home_score"],
            event["away_score"],
            event["event_time"],
        ),
    )

    conn.commit()
    cur.close()
    conn.close()

print("Listening for game updates...")

for message in consumer:
    event = message.value
    insert_game_event(event)
    print(f"Inserted game event: {event}")