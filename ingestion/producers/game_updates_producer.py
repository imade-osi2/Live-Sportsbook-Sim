import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

sample_updates = [
    {
        "game_event_id": "game_001",
        "game_id": "nba_002",
        "game_status": "in_progress",
        "home_score": 24,
        "away_score": 20,
        "event_time": "2026-04-16T18:25:00"
    },
    {
        "game_event_id": "game_002",
        "game_id": "nba_003",
        "game_status": "in_progress",
        "home_score": 31,
        "away_score": 29,
        "event_time": "2026-04-16T18:26:00"
    }
]

for event in sample_updates:
    producer.send("game_updates", event)
    print(f"Sent: {event}")
    time.sleep(1)

producer.flush()
producer.close()