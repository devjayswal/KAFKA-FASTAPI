from kafka import KafkaProducer
from fastapi import FastAPI
from produce_schema import ProduceMessage
from fastapi import HTTPException
import json

#constants
KAFKA_BROKER_URL = "127.0.0.1:9092"
KAFKA_TOPIC = "fastapi-topic"
PRODUCER_CLIENT_ID = "fastapi-producer"

def serializer(message):
    return json.dumps(message).encode()


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=serializer,
    client_id=PRODUCER_CLIENT_ID,
    acks='all',              # Ensure all replicas acknowledge the message
    retries=5                # Retry sending if it fails
)


def produce_kafka_message(messageRequest: ProduceMessage):
    try:
        print(f"Attempting to send message to Kafka: {messageRequest.message}")
        producer.send(KAFKA_TOPIC, messageRequest.model_dump())
        producer.flush() #ENSURE MESSAGE IS SENT
        print(f"Successfully sent message to topic {KAFKA_TOPIC}")
    except Exception as e:
        print(f"Error producing message to Kafka: {e}")
