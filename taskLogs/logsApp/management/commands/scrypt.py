from django.core.management.base import BaseCommand
from logsApp.kafka_consumer import KafkaMessageConsumer


class Command(BaseCommand):
    help = 'Launches Listener for Kafka messages'

    def handle(self, *args, **options):
        kafka_broker = 'kafka:9092'
        kafka_topics = ['task_created', 'task_deleted', 'task_updated']
        consumer = KafkaMessageConsumer(kafka_broker, kafka_topics)
        consumer.consume_messages()
