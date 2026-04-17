import json
from kafka import KafkaConsumer
from ingestion.api_clients.postgres_client import get_postgres_connection


consumer = KafkaConsumer(
    "bets",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="bets-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)


def insert_bet_event(event):
    conn = get_postgres_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO raw.bet_events_stream (
            bet_id,
            user_id,
            game_id,
            market_type,
            selection,
            stake,
            odds,
            bet_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (bet_id) DO NOTHING
    """

    cur.execute(
        insert_sql,
        (
            event["bet_id"],
            event["user_id"],
            event["game_id"],
            event["market_type"],
            event["selection"],
            event["stake"],
            event["odds"],
            event["bet_time"],
        ),
    )

    conn.commit()
    cur.close()
    conn.close()


print("Listening for bet events...")

for message in consumer:
    event = message.value
    insert_bet_event(event)
    print(f"Inserted into Postgres: {event}")