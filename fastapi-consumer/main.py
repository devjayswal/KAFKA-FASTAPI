from fastapi import FastAPI
import asyncio
from kafka import KafkaConsumer
import json
from models.Message import MessageSchema
from config import collection
from pydantic import ValidationError

#constants
KAFKA_BROKER_URL = "127.0.0.1:9092"
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
    try:
        print(f"Connecting to Kafka at {KAFKA_BROKER_URL}...")
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER_URL,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=CONSUMER_CONSUMER_ID,
            value_deserializer=deserializer,
            request_timeout_ms=30000
        )
        print("Kafka Consumer created successfully!")
        return consumer
    except Exception as e:
        print(f"Failed to create Kafka consumer: {e}")
        return None

async def poll_consumer():
    print(f"Started polling Kafka topic: {KAFKA_TOPIC}")
    consumer = None
    try:
        while not stop_polling_event.is_set():
            if consumer is None:
                consumer = create_kafka_consumer()
                if consumer is None:
                    await asyncio.sleep(5)
                    continue

            try:
                # Run poll in a thread to avoid blocking the event loop
                records = await asyncio.to_thread(consumer.poll, timeout_ms=1000)
                if records:
                    print(f"Fetched {len(records)} batches from Kafka")
                    for record in records.values():
                        for message in record:
                            try:
                                if message.value:
                                    validated_msg = MessageSchema(**message.value)
                                    collection.insert_one(validated_msg.model_dump())
                                    print(f"✅ SUCCESS: Saved to MongoDB: {validated_msg.message}")
                            except Exception as e:
                                print(f"❌ DATABASE ERROR: {e}")
            except Exception as poll_error:
                print(f"Poll error: {poll_error}")
                consumer.close()
                consumer = None  # Force recreation on next loop
                await asyncio.sleep(2)
            
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Critical error in polling loop: {e}")
    finally:
        print("Stopping consumer polling")
        if consumer:
            consumer.close()

tasklist = []
@app.get("/trigger")
async def trigger_polling():
    global tasklist
    tasklist = [t for t in tasklist if not t.done()]

    if not tasklist:
        stop_polling_event.clear()
        task = asyncio.create_task(poll_consumer())
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