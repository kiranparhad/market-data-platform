import json
import random
import time
from datetime import date, timedelta

from confluent_kafka import Producer

KAFKA_BROKER = "localhost:29092"
TOPIC = "corporate-actions"

producer = Producer({"bootstrap.servers": KAFKA_BROKER})

ACTIONS = [
    {
        "action_type": "SPLIT",
        "ticker": "AAPL",
        "ratio": 4.0,
        "index_id": None,
    },
    {
        "action_type": "ADDITION",
        "ticker": "NVDA",
        "ratio": None,
        "index_id": "SPX500",
    },
    {
        "action_type": "REMOVAL",
        "ticker": "GE",
        "ratio": None,
        "index_id": "SPX500",
    },
    {
        "action_type": "SPLIT",
        "ticker": "TSLA",
        "ratio": 3.0,
        "index_id": None,
    },
]

action_counter = 0


def generate_action():
    global action_counter
    action_counter += 1
    template = random.choice(ACTIONS)
    today = date.today()

    action = {
        "action_id": f"CA-2026-{action_counter:03d}",
        "ticker": template["ticker"],
        "action_type": template["action_type"],
        "effective_date": str(today + timedelta(days=random.randint(5, 30))),
        "announced_date": str(today),
        "status": random.choice(["CONFIRMED", "PENDING"]),
    }

    if template["ratio"] is not None:
        action["ratio"] = template["ratio"]
    if template["index_id"] is not None:
        action["index_id"] = template["index_id"]

    return action


def delivery_report(err, msg):
    if err:
        print(f"FAILED: {err}")
    else:
        print(f"Delivered: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


if __name__ == "__main__":
    print("Publishing corporate actions every 15s... (Ctrl+C to stop)")
    try:
        while True:
            action = generate_action()
            producer.produce(
                topic=TOPIC,
                key=action["ticker"],
                value=json.dumps(action),
                callback=delivery_report,
            )
            producer.flush()
            print(
                f"Published: {action['action_id']} - {action['action_type']} on {action['ticker']}"
            )
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nStopping...")
