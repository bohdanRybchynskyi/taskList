import json

from kafka import KafkaConsumer
from logsApp.models import LogEntry


class KafkaMessageConsumer:
    def __init__(self, kafka_broker, topics):
        self.kafka_broker = kafka_broker
        self.topics = topics

    def consume_messages(self):
        consumer = KafkaConsumer(
            *self.topics,
            bootstrap_servers=self.kafka_broker,
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id='task_manager_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        try:
            for message in consumer:
                log_data = message.value
                LogEntry.objects.create(**log_data)
        finally:
            consumer.close()
