import json
from kafka import KafkaConsumer


consumer = KafkaConsumer(
    "bets",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="bets-consumer-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)


print("Listening for bet events...")

for message in consumer:
    print(f"Received: {message.value}")