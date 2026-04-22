import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

sample_odds = [
    {
        "odds_event_id": "odds_101",
        "game_id": "nba_002",
        "sportsbook": "demo_book",
        "market_type": "moneyline",
        "home_odds": -120,
        "away_odds": 105,
        "spread": -2.5,
        "total_points": 221.5,
        "event_time": "2026-04-20T17:30:00"
    },
    {
        "odds_event_id": "odds_102",
        "game_id": "nba_002",
        "sportsbook": "demo_book",
        "market_type": "moneyline",
        "home_odds": -130,
        "away_odds": 110,
        "spread": -3.0,
        "total_points": 222.0,
        "event_time": "2026-04-20T18:45:00"
    },
    {
        "odds_event_id": "odds_103",
        "game_id": "nba_002",
        "sportsbook": "demo_book",
        "market_type": "moneyline",
        "home_odds": -140,
        "away_odds": 120,
        "spread": -3.5,
        "total_points": 223.5,
        "event_time": "2026-04-20T19:20:00"
    },
    {
        "odds_event_id": "odds_104",
        "game_id": "nba_003",
        "sportsbook": "demo_book",
        "market_type": "spread",
        "home_odds": -110,
        "away_odds": -110,
        "spread": -4.5,
        "total_points": 228.5,
        "event_time": "2026-04-20T17:35:00"
    },
    {
        "odds_event_id": "odds_105",
        "game_id": "nba_003",
        "sportsbook": "demo_book",
        "market_type": "spread",
        "home_odds": -115,
        "away_odds": -105,
        "spread": -5.0,
        "total_points": 229.0,
        "event_time": "2026-04-20T18:50:00"
    },
    {
        "odds_event_id": "odds_106",
        "game_id": "nba_003",
        "sportsbook": "demo_book",
        "market_type": "spread",
        "home_odds": -120,
        "away_odds": 100,
        "spread": -5.5,
        "total_points": 230.0,
        "event_time": "2026-04-20T19:25:00"
    }
]

for event in sample_odds:
    producer.send("odds_updates", event)
    print(f"Sent: {event}")
    time.sleep(1)

producer.flush()
producer.close()