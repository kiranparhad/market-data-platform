import json
import time
from datetime import date

from confluent_kafka import Producer

KAFKA_BROKER = "localhost:29092"
TOPIC = "reference-data"

producer = Producer({"bootstrap.servers": KAFKA_BROKER})


def generate_snapshot(version):
    return {
        "index_id": "SPX500",
        "effective_date": str(date.today()),
        "version": version,
        "constituents": [
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc",
                "weight": 0.072,
                "shares_outstanding": 15204137000,
                "sector": "Technology",
            },
            {
                "ticker": "MSFT",
                "company_name": "Microsoft Corp",
                "weight": 0.068,
                "shares_outstanding": 7432654000,
                "sector": "Technology",
            },
            {
                "ticker": "AMZN",
                "company_name": "Amazon.com Inc",
                "weight": 0.035,
                "shares_outstanding": 10495456000,
                "sector": "Consumer Discretionary",
            },
            {
                "ticker": "GOOGL",
                "company_name": "Alphabet Inc",
                "weight": 0.045,
                "shares_outstanding": 5893421000,
                "sector": "Technology",
            },
            {
                "ticker": "TSLA",
                "company_name": "Tesla Inc",
                "weight": 0.022,
                "shares_outstanding": 3185510000,
                "sector": "Consumer Discretionary",
            },
        ],
    }


def delivery_report(err, msg):
    if err:
        print(f"FAILED: {err}")
    else:
        print(f"Delivered: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


if __name__ == "__main__":
    print("Publishing reference snapshots every 30s... (Ctrl+C to stop)")
    version = 1
    try:
        while True:
            snapshot = generate_snapshot(version)
            producer.produce(
                topic=TOPIC,
                key=snapshot["index_id"],
                value=json.dumps(snapshot),
                callback=delivery_report,
            )
            producer.flush()
            print(f"Published snapshot v{version}")
            version += 1
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopping...")
