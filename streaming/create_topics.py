from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({"bootstrap.servers": "localhost:29092"})

topics = [
    NewTopic("market-ticks", num_partitions=3, replication_factor=1),
    NewTopic("reference-data", num_partitions=1, replication_factor=1),
    NewTopic("corporate-actions", num_partitions=1, replication_factor=1),
]

futures = admin.create_topics(topics)

for topic, future in futures.items():
    try:
        future.result()
        print(f"Topic '{topic}' created successfully")
    except Exception as e:
        print(f"Topic '{topic}': {e}")
