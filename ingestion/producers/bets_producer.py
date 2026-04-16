import json
import time
from kafka import KafkaProducer


producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


sample_bets = [
    {
        "bet_id": "bet_001",
        "user_id": "user_101",
        "game_id": "nba_002",
        "market_type": "moneyline",
        "selection": "Hornets",
        "stake": 25.0,
        "odds": -110,
        "bet_time": "2026-04-16T18:15:00"
    },
    {
        "bet_id": "bet_002",
        "user_id": "user_102",
        "game_id": "nba_003",
        "market_type": "spread",
        "selection": "Warriors -4.5",
        "stake": 40.0,
        "odds": -105,
        "bet_time": "2026-04-16T18:16:00"
    }
]


for bet in sample_bets:
    producer.send("bets", bet)
    print(f"Sent: {bet}")
    time.sleep(1)

producer.flush()
producer.close()