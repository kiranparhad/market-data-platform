import json
import logging

from confluent_kafka import Consumer, KafkaError

from ingestion.services.tick_service import TickService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = "localhost:29092"
TOPIC = "market-ticks"

consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_BROKER,
        "group.id": "tick-ingestion-group",
        "auto.offset.reset": "earliest",
    }
)

tick_service = TickService()


if __name__ == "__main__":
    consumer.subscribe([TOPIC])
    print("Tick consumer started... (Ctrl+C to stop)")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Kafka error: %s", msg.error())
                continue

            raw_data = json.loads(msg.value().decode("utf-8"))
            success, error = tick_service.ingest(raw_data)

            if success:
                logger.info(
                    "Ingested: %s @ %s [partition %s, offset %s]",
                    raw_data["ticker"],
                    raw_data["price"],
                    msg.partition(),
                    msg.offset(),
                )
            else:
                logger.warning(
                    "Rejected: %s [partition %s, offset %s]",
                    error,
                    msg.partition(),
                    msg.offset(),
                )

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        consumer.close()
