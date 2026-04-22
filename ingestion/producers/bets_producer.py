import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

sample_bets = [
    {
        "bet_id": "bet_101",
        "user_id": "user_201",
        "game_id": "nba_002",
        "market_type": "moneyline",
        "selection": "Hornets",
        "stake": 25.0,
        "odds": -120,
        "bet_time": "2026-04-20T17:40:00"
    },
    {
        "bet_id": "bet_102",
        "user_id": "user_202",
        "game_id": "nba_002",
        "market_type": "spread",
        "selection": "Hornets -2.5",
        "stake": 40.0,
        "odds": -110,
        "bet_time": "2026-04-20T18:10:00"
    },
    {
        "bet_id": "bet_103",
        "user_id": "user_203",
        "game_id": "nba_003",
        "market_type": "moneyline",
        "selection": "Warriors",
        "stake": 35.0,
        "odds": -110,
        "bet_time": "2026-04-20T17:45:00"
    },
    {
        "bet_id": "bet_104",
        "user_id": "user_204",
        "game_id": "nba_003",
        "market_type": "spread",
        "selection": "Warriors -4.5",
        "stake": 50.0,
        "odds": -105,
        "bet_time": "2026-04-20T18:15:00"
    },
    {
        "bet_id": "bet_105",
        "user_id": "user_205",
        "game_id": "nba_002",
        "market_type": "moneyline",
        "selection": "Magic",
        "stake": 20.0,
        "odds": 110,
        "bet_time": "2026-04-20T19:10:00"
    },
    {
        "bet_id": "bet_106",
        "user_id": "user_206",
        "game_id": "nba_003",
        "market_type": "spread",
        "selection": "Suns +5.5",
        "stake": 60.0,
        "odds": 100,
        "bet_time": "2026-04-20T19:18:00"
    }
]

for bet in sample_bets:
    producer.send("bets", bet)
    print(f"Sent: {bet}")
    time.sleep(1)

producer.flush()
producer.close()