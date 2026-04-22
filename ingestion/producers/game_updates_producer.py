import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

sample_updates = [
    {
        "game_event_id": "game_101",
        "game_id": "nba_002",
        "game_status": "scheduled",
        "home_score": 0,
        "away_score": 0,
        "event_time": "2026-04-20T18:00:00"
    },
    {
        "game_event_id": "game_102",
        "game_id": "nba_003",
        "game_status": "scheduled",
        "home_score": 0,
        "away_score": 0,
        "event_time": "2026-04-20T18:01:00"
    },
    {
        "game_event_id": "game_103",
        "game_id": "nba_002",
        "game_status": "in_progress",
        "home_score": 18,
        "away_score": 14,
        "event_time": "2026-04-20T19:05:00"
    },
    {
        "game_event_id": "game_104",
        "game_id": "nba_003",
        "game_status": "in_progress",
        "home_score": 24,
        "away_score": 20,
        "event_time": "2026-04-20T19:06:00"
    },
    {
        "game_event_id": "game_105",
        "game_id": "nba_002",
        "game_status": "final",
        "home_score": 102,
        "away_score": 97,
        "event_time": "2026-04-20T21:30:00"
    }
]

for event in sample_updates:
    producer.send("game_updates", event)
    print(f"Sent: {event}")
    time.sleep(1)

producer.flush()
producer.close()