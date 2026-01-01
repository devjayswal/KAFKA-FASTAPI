# Event-Driven Architecture (EDA) with FastAPI and Kafka

This project demonstrates a simple Event-Driven Architecture (EDA) using FastAPI as both a producer and a consumer, with Apache Kafka as the message broker.

## Project Structure

- **fastapi-producer/**: A FastAPI application that receives messages via a POST endpoint and produces them to a Kafka topic.
- **fastapi-consumer/**: A FastAPI application that polls and consumes messages from the Kafka topic.
- **docker-compose.yml**: Configuration to spin up Kafka and Zookeeper containers.

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [Python 3.10+](https://www.python.org/)
- [Virtualenv](https://virtualenv.pypa.io/en/latest/) (optional but recommended)

## Getting Started

### 1. Start Kafka and Zookeeper

Use Docker Compose to start the Kafka broker and Zookeeper:

```bash
docker-compose up -d
```

### 2. Set Up Python Environment

Create and activate a virtual environment, then install the dependencies:

```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment (Windows)
.\myenv\Scripts\activate

# Activate virtual environment (Linux/macOS)
source myenv/bin/activate

# Install dependencies
pip install fastapi uvicorn kafka-python-ng pydantic
```

### 3. Run the Producer

Navigate to the `fastapi-producer` directory and start the server:

```bash
cd fastapi-producer
uvicorn main:app --reload --port 8000
```

The producer API will be available at `http://localhost:8000`. You can access the Swagger UI at `http://localhost:8000/docs`.

### 4. Run the Consumer

Navigate to the `fastapi-consumer` directory and start the server:

```bash
cd fastapi-consumer
uvicorn main:app --reload --port 8001
```

The consumer will start polling the `fastapi-topic` and log received messages to the console.

## API Endpoints

### Producer

- **POST** `/produce/message`: Sends a message to the Kafka topic.
  - **Payload**:
    ```json
    {
      "message": "Hello Kafka!"
    }
    ```

## Technologies Used

- **FastAPI**: Web framework for building APIs.
- **Apache Kafka**: Distributed event streaming platform.
- **Kafka-python-ng**: Python client for Apache Kafka.
- **Pydantic**: Data validation and settings management.
- **Docker**: Containerization platform.
