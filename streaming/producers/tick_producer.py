import json
import random
import time
from datetime import datetime, timezone

from confluent_kafka import Producer

KAFKA_BROKER = "localhost:29092"
TOPIC = "market-ticks"

TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"]
EXCHANGES = [
    {"source_id": "XNAS", "source_name": "NASDAQ"},
    {"source_id": "XNYS", "source_name": "NYSE"},
]
TICK_TYPES = ["TRADE", "BID", "ASK"]

# Simulated base prices
PRICES = {"AAPL": 189.50, "MSFT": 441.30, "AMZN": 186.20, "GOOGL": 176.80, "TSLA": 248.50}

producer = Producer({"bootstrap.servers": KAFKA_BROKER})


def generate_tick():
    ticker = random.choice(TICKERS)
    exchange = random.choice(EXCHANGES)
    base_price = PRICES[ticker]
    # Simulate small price movement: +/- 0.5%
    price = round(base_price * (1 + random.uniform(-0.005, 0.005)), 2)
    PRICES[ticker] = price  # update base for next tick

    return {
        "ticker": ticker,
        "price": price,
        "volume": random.randint(0, 5000),
        "tick_type": random.choice(TICK_TYPES),
        "source_id": exchange["source_id"],
        "source_name": exchange["source_name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def delivery_report(err, msg):
    if err:
        print(f"FAILED: {err}")
    else:
        print(f"Delivered: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


if __name__ == "__main__":
    print("Starting tick producer... (Ctrl+C to stop)")
    try:
        while True:
            tick = generate_tick()
            producer.produce(
                topic=TOPIC,
                key=tick["ticker"],
                value=json.dumps(tick),
                callback=delivery_report,
            )
            producer.poll(0)
            time.sleep(0.5)  # 2 ticks per second
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        producer.flush()
