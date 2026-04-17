import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

sample_odds = [
    {
        "odds_event_id": "odds_001",
        "game_id": "nba_002",
        "sportsbook": "demo_book",
        "market_type": "moneyline",
        "home_odds": -120,
        "away_odds": 105,
        "spread": -2.5,
        "total_points": 221.5,
        "event_time": "2026-04-16T18:20:00"
    },
    {
        "odds_event_id": "odds_002",
        "game_id": "nba_003",
        "sportsbook": "demo_book",
        "market_type": "spread",
        "home_odds": -110,
        "away_odds": -110,
        "spread": -4.5,
        "total_points": 228.5,
        "event_time": "2026-04-16T18:21:00"
    }
]

for event in sample_odds:
    producer.send("odds_updates", event)
    print(f"Sent: {event}")
    time.sleep(1)

producer.flush()
producer.close()