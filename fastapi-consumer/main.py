from fastapi import FastAPI
import asyncio
from kafka import KafkaConsumer
import json
from models.Message import MessageSchema
from config import collection
from pydantic import ValidationError

#constants
KAFKA_BROKER_URL = "localhost:9092"
KAFKA_TOPIC = "fastapi-topic"
CONSUMER_CONSUMER_ID = "fastapi-consumer"

stop_polling_event  = asyncio.Event()

app = FastAPI()


def deserializer(message):
    if message is None:
        return None
    try:
        return json.loads(message.decode('utf-8'))
    except json.JSONDecodeError:
        print("unable to decode message")
        return None


def create_kafka_consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=CONSUMER_CONSUMER_ID,
        value_deserializer=deserializer,
    )
    return consumer

async def poll_consumer(consumer:KafkaConsumer):
    print(f"Started polling Kafka topic: {KAFKA_TOPIC}")
    try:
        while not stop_polling_event.is_set():
            records = await asyncio.to_thread(consumer.poll(), timeout_ms=1000)
            if records:
                print(f"Polled {len(records)} record batches")
                for record in records.values():
                    for message in record:
                        try:
                            print(f"Processing message from partition {message.partition} at offset {message.offset}")
                            if message.value:
                                validated_msg = MessageSchema(**message.value)
                                collection.insert_one(validated_msg.model_dump())
                                print(f"Saved to MongoDB and Received the message: {validated_msg.message} from the topic of {message.topic}")
                        except ValidationError as ve:
                            print(f"Validation error for message from {message.topic}: {ve}")
                        except Exception as e:
                            print(f"Error processing message: {e}")
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error polling messages from Kafka: {e}")
    finally:
        print("Stopping consumer polling")
        consumer.close() 
tasklist = []
@app.get("/trigger")
async def trigger_polling():
    global tasklist
    # Clean up finished tasks
    tasklist = [t for t in tasklist if not t.done()]

    if not tasklist:
        stop_polling_event.clear() # reset the flag
        consumer = create_kafka_consumer()
        task = asyncio.create_task(poll_consumer(consumer=consumer))
        tasklist.append(task)

        return {"message": "Started polling Kafka topic."}
    else:
        return {"message": "Polling is already running."}
    

@app.get("/stop-trigger")
async def stop_polling():
    stop_polling_event.set()
    if tasklist:
        tasklist.pop()

    return {"message": "Stopped polling Kafka topic."}