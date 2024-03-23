from kafka import KafkaProducer
import json

class KafkaMessageProducer:
    def __init__(self, kafka_broker, topic):
        self.producer = KafkaProducer(bootstrap_servers=kafka_broker,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.topic = topic

    def send_message(self, message):
        try:
            self.producer.send(self.topic, value=message)
            self.producer.flush()
            print("Message sent successfully!")
        except Exception as e:
            print(f"Failed to send message: {e}")

    def close(self):
        self.producer.close()