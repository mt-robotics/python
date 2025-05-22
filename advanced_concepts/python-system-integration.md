# Python System Integration and Resource Management

## Introduction

System integration involves connecting different computing systems and software applications to act as a coordinated whole, while proper resource management ensures these integrations operate efficiently and reliably. This guide covers essential techniques and patterns for Python system integration, including working with message queues, implementing microservices, managing inter-process communication, and handling system resources effectively.

## Table of Contents

- [Python System Integration and Resource Management](#python-system-integration-and-resource-management)
  - [Introduction](#introduction)
  - [Table of Contents](#table-of-contents)
  - [System Integration Fundamentals](#system-integration-fundamentals)
    - [Integration Patterns](#integration-patterns)
    - [Integration Challenges](#integration-challenges)
    - [Python's Integration Strengths](#pythons-integration-strengths)
  - [Message Queues and Brokers](#message-queues-and-brokers)
    - [RabbitMQ with Pika](#rabbitmq-with-pika)
    - [Kafka with confluent-kafka](#kafka-with-confluent-kafka)
    - [Redis as a Message Broker](#redis-as-a-message-broker)
    - [Celery for Distributed Task Queue](#celery-for-distributed-task-queue)
  - [Microservices Architecture](#microservices-architecture)
    - [Building Microservices with FastAPI](#building-microservices-with-fastapi)
    - [Service Discovery with Consul](#service-discovery-with-consul)
    - [API Gateway with Traefik](#api-gateway-with-traefik)
    - [Circuit Breaker Pattern](#circuit-breaker-pattern)
    - [Configuration Management](#configuration-management)
  - [API Design and Implementation](#api-design-and-implementation)
    - [RESTful API Best Practices](#restful-api-best-practices)
  - [Inter-Process Communication](#inter-process-communication)
    - [ZeroMQ for IPC](#zeromq-for-ipc)
    - [Named Pipes](#named-pipes)
    - [Shared Memory](#shared-memory)
  - [Distributed Systems Patterns](#distributed-systems-patterns)
    - [Service Discovery](#service-discovery)
    - [Circuit Breaker](#circuit-breaker)
    - [Bulkhead Pattern](#bulkhead-pattern)
    - [Retry Pattern](#retry-pattern)
  - [Event-Driven Architecture](#event-driven-architecture)
    - [Event Publishing/Subscribing](#event-publishingsubscribing)
    - [Event Sourcing](#event-sourcing)
    - [CQRS Pattern](#cqrs-pattern)
  - [Integration Testing](#integration-testing)
    - [Testing Microservices](#testing-microservices)
    - [Testing Message Queues](#testing-message-queues)
    - [Monitoring and Observability](#monitoring-and-observability)
      - [Prometheus Metrics](#prometheus-metrics)
      - [Distributed Tracing](#distributed-tracing)
      - [Centralized Logging](#centralized-logging)
    - [Best Practices](#best-practices)
      - [Loose Coupling](#loose-coupling)
    - [Error Handling](#error-handling)
    - [Documentation](#documentation)
    - [Security](#security)

## System Integration Fundamentals

### Integration Patterns

Common integration patterns used in Python applications:

1. **File Transfer**: Systems exchange files
2. **Shared Database**: Systems share a common database
3. **Remote Procedure Call**: Systems call each other's functions
4. **Messaging**: Systems communicate via message queues
5. **API Integration**: Systems expose and consume APIs
6. **Event-Driven**: Systems react to events

### Integration Challenges

Typical challenges in system integration:

- **Data Format Compatibility**: Different systems use different data formats
- **Timing**: Systems may process data at different speeds
- **Reliability**: Handling failures in the integrated system
- **Scalability**: Ensuring the integrated system can handle load
- **Security**: Securing communication between systems
- **Versioning**: Managing changes to interfaces over time

### Python's Integration Strengths

Python offers several advantages for integration:

- **Rich Ecosystem**: Libraries for nearly every integration need
- **Flexibility**: Supports multiple programming paradigms
- **Rapid Development**: Speeds up integration development
- **Cross-Platform**: Runs on various operating systems
- **Extensive Standard Library**: Built-in modules for common tasks

## Message Queues and Brokers

### RabbitMQ with Pika

RabbitMQ is a popular message broker that implements AMQP:

```python
import pika
import json

# Producer
def publish_message(queue_name, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Declare the queue (creates if not exists)
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    
    print(f" [x] Sent {message}")
    connection.close()

# Consumer
def consume_messages(queue_name, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Declare the queue (creates if not exists)
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )
    
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

# Example callback function
def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f" [x] Received {message}")
        # Process the message...
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        # Nack the message so it goes back to the queue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### Kafka with confluent-kafka

Apache Kafka is a distributed streaming platform:

```python
from confluent_kafka import Producer, Consumer
import json

# Producer
def produce_message(topic, message):
    # Configure the producer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'python-producer'
    }
    producer = Producer(conf)
    
    # Produce message
    producer.produce(
        topic,
        key=str(message.get('id', '')),
        value=json.dumps(message)
    )
    producer.flush()

# Consumer
def consume_messages(topic, group_id):
    # Configure the consumer
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    
    # Subscribe to topic
    consumer.subscribe([topic])
    
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            
            # Process message
            try:
                message = json.loads(msg.value().decode('utf-8'))
                print(f"Received message: {message}")
                # Process the message...
                
            except Exception as e:
                print(f"Error processing message: {e}")
    
    except KeyboardInterrupt:
        pass
    
    finally:
        # Close down consumer
        consumer.close()
```

### Redis as a Message Broker

Redis can be used as a lightweight message broker:

```python
import redis
import json
import time

# Setup Redis connection
r = redis.Redis(host='localhost', port=6379, db=0)

# Producer using Redis List
def publish_to_queue(queue_name, message):
    r.lpush(queue_name, json.dumps(message))
    print(f"Published message: {message}")

# Consumer using Redis List
def consume_from_queue(queue_name):
    while True:
        # BRPOP blocks until a message is available
        message = r.brpop(queue_name, timeout=1)
        if message:
            # message is a tuple (queue_name, value)
            try:
                data = json.loads(message[1])
                print(f"Received message: {data}")
                # Process the message...
            except Exception as e:
                print(f"Error processing message: {e}")
        else:
            # No message available
            time.sleep(0.1)

# Redis Pub/Sub model
def publish_event(channel, message):
    r.publish(channel, json.dumps(message))
    print(f"Published event to {channel}: {message}")

def subscribe_to_events(channel):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                print(f"Received event from {channel}: {data}")
                # Process the event...
            except Exception as e:
                print(f"Error processing event: {e}")
```

### Celery for Distributed Task Queue

Celery is a distributed task queue:

```python
# tasks.py
from celery import Celery

# Create the Celery app
app = Celery(
    'tasks',
    broker='pyamqp://guest@localhost//',
    backend='redis://localhost'
)

# Define a task
@app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5}
)
def process_data(self, data):
    try:
        # Process the data...
        result = {'status': 'success', 'processed_data': data}
        return result
    except Exception as e:
        print(f"Error processing data: {e}")
        raise

# To run the worker:
# celery -A tasks worker --loglevel=info

# To call the task:
def call_task():
    result = process_data.delay({'id': 123, 'value': 'test'})
    # If you need the result
    task_result = result.get(timeout=10)  # Wait up to 10 seconds
    print(f"Task result: {task_result}")
```

## Microservices Architecture

### Building Microservices with FastAPI

FastAPI is a modern framework for building APIs:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI(title="User Service")

# Data model
class User(BaseModel):
    id: int
    name: str
    email: str

# In-memory storage (replace with database in production)
users_db = {}

@app.post("/users/", response_model=User)
async def create_user(user: User):
    if user.id in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    users_db[user.id] = user.dict()
    return user

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

@app.get("/users/")
async def read_users():
    return list(users_db.values())

# Service-to-service communication
async def get_orders(user_id: int):
    # Call the Order Service
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://orders-service:8001/orders/user/{user_id}")
        response.raise_for_status()
        return response.json()

@app.get("/users/{user_id}/orders")
async def read_user_orders(user_id: int):
    # First, check if user exists
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        orders = await get_orders(user_id)
        return {"user": users_db[user_id], "orders": orders}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"Order service unavailable: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Service Discovery with Consul

Using Consul for service discovery:

```python
import consul
import socket
import time
import uuid
import atexit

class ServiceRegistry:
    def __init__(self, service_name, host=None, port=None, tags=None):
        self.service_name = service_name
        self.service_id = f"{service_name}-{uuid.uuid4()}"
        self.host = host or socket.gethostname()
        self.port = port or 8000
        self.tags = tags or []
        
        # Connect to Consul
        self.consul = consul.Consul()
        
        # Register cleanup on exit
        atexit.register(self.deregister)
    
    def register(self):
        """Register service with Consul"""
        self.consul.agent.service.register(
            name=self.service_name,
            service_id=self.service_id,
            address=self.host,
            port=self.port,
            tags=self.tags,
            check=consul.Check.http(
                url=f"http://{self.host}:{self.port}/health",
                interval="10s",
                timeout="5s"
            )
        )
        print(f"Registered service: {self.service_name} ({self.service_id})")
    
    def deregister(self):
        """Deregister service from Consul"""
        self.consul.agent.service.deregister(self.service_id)
        print(f"Deregistered service: {self.service_name} ({self.service_id})")
    
    def get_service(self, service_name):
        """Discover a service by name"""
        index, services = self.consul.catalog.service(service_name)
        if not services:
            return None
        
        # Return a random instance (for simple load balancing)
        import random
        service = random.choice(services)
        return {
            'address': service['ServiceAddress'] or service['Address'],
            'port': service['ServicePort'],
            'tags': service['ServiceTags']
        }

# Usage
if __name__ == "__main__":
    # Register this service
    registry = ServiceRegistry("user-service", port=8000, tags=["api", "v1"])
    registry.register()
    
    # Discover another service
    try:
        while True:
            order_service = registry.get_service("order-service")
            if order_service:
                print(f"Found order service at {order_service['address']}:{order_service['port']}")
            else:
                print("Order service not found")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down...")
```

### API Gateway with Traefik

Configuring Traefik as an API gateway:

```yaml
# docker-compose.yml
version: '3'

services:
  traefik:
    image: traefik:v2.5
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  user-service:
    build: ./user-service
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.user-service.rule=PathPrefix(`/api/users`)"
      - "traefik.http.routers.user-service.entrypoints=web"
      - "traefik.http.middlewares.user-strip.stripprefix.prefixes=/api/users"
      - "traefik.http.routers.user-service.middlewares=user-strip"

  order-service:
    build: ./order-service
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.order-service.rule=PathPrefix(`/api/orders`)"
      - "traefik.http.routers.order-service.entrypoints=web"
      - "traefik.http.middlewares.order-strip.stripprefix.prefixes=/api/orders"
      - "traefik.http.routers.order-service.middlewares=order-strip"
```

### Circuit Breaker Pattern

Implementing circuit breaker with `pybreaker`:

```python
import pybreaker
import httpx
import time
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Initialize circuit breaker
order_service_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  # Number of failures before opening the circuit
    reset_timeout=30,  # Seconds until attempting to close the circuit
    exclude=[httpx.ConnectTimeout],  # Exceptions to ignore
    state_storage=pybreaker.CircuitMemoryStorage()
)

@order_service_breaker
async def get_orders(user_id):
    """Call the order service with circuit breaker protection"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://order-service:8001/orders/user/{user_id}",
            timeout=5.0  # Set a timeout
        )
        response.raise_for_status()
        return response.json()

@app.get("/users/{user_id}/orders")
async def read_user_orders(user_id: int):
    try:
        # Circuit breaker will track failures and open if necessary
        orders = await get_orders(user_id)
        return {"user_id": user_id, "orders": orders}
    except pybreaker.CircuitBreakerError:
        # Circuit is open
        return {"user_id": user_id, "orders": [], "message": "Order service is currently unavailable"}
    except httpx.HTTPError as e:
        # Other HTTP errors
        raise HTTPException(status_code=503, detail=f"Order service error: {str(e)}")
```

### Configuration Management

Managing configuration across microservices:

```python
import os
import yaml
import json
import consul
from pydantic import BaseSettings
from typing import Dict, Any, Optional

class ServiceSettings(BaseSettings):
    """Base settings class with multiple providers"""
    
    # Service identification
    service_name: str
    service_version: str = "1.0.0"
    
    # Network settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = ""
    
    # Additional settings
    log_level: str = "INFO"
    debug: bool = False
    
    @classmethod
    def from_file(cls, file_path: str):
        """Load settings from a file (YAML or JSON)"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            elif file_path.endswith('.json'):
                config_data = json.load(f)
            else:
                raise ValueError("Unsupported config file format")
        
        return cls(**config_data)
    
    @classmethod
    def from_consul(cls, consul_host: str = "localhost", consul_port: int = 8500, 
                   key_prefix: str = "config/"):
        """Load settings from Consul KV store"""
        c = consul.Consul(host=consul_host, port=consul_port)
        index, data = c.kv.get(key_prefix, recurse=True)
        
        if not data:
            raise ValueError(f"No configuration found in Consul at {key_prefix}")
        
        config_data = {}
        for item in data:
            key = item["Key"].replace(key_prefix, "")
            value = item["Value"].decode("utf-8") if item["Value"] else None
            config_data[key] = value
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return self.dict()

# Usage
def load_settings() -> ServiceSettings:
    """Load settings from various sources with priority"""
    
    # Priority order: Environment variables > Consul > Config file > Defaults
    
    # Try to get config file path from environment
    config_file = os.environ.get("CONFIG_FILE")
    
    try:
        # Try Consul if configured in environment
        if os.environ.get("CONSUL_HOST"):
            return ServiceSettings.from_consul(
                consul_host=os.environ.get("CONSUL_HOST"),
                consul_port=int(os.environ.get("CONSUL_PORT", "8500")),
                key_prefix=os.environ.get("CONSUL_KEY_PREFIX", "config/")
            )
    except Exception as e:
        print(f"Failed to load config from Consul: {e}")
    
    try:
        # Try config file
        if config_file and os.path.exists(config_file):
            return ServiceSettings.from_file(config_file)
    except Exception as e:
        print(f"Failed to load config from file: {e}")
    
    # Fall back to environment variables and defaults
    return ServiceSettings()
```

## API Design and Implementation

### RESTful API Best Practices

Building well-designed REST APIs:

```python
from fastapi import FastAPI, HTTPException, Depends, Query, Path, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Product API",
    description="API for managing products",
    version="1.0.0"
)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Data models
class ProductBase(BaseModel):
    name: str = Field(..., example="Smartphone")
    description: Optional[str] = Field(None, example="Latest smartphone model")
    price: float = Field(..., gt=0, example=799.99)
    category: str = Field(..., example="Electronics")

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Smartphone",
                "description": "Latest smartphone model",
                "price": 799.99,
                "category": "Electronics",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-02T00:00:00"
            }
        }

class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Product]

# Simulated DB (replace with real database in production)
products_db = []

# Helper functions
def get_product(product_id: int):
    for product in products_db:
        if product["id"] == product_id:
            return product
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real application, validate the token and get the user
    # This is a simplified example
    return {"username": "john_doe"}

# Endpoints
@app.post(
    "/products/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Create a new product with the provided details"
)
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    product_id = len(products_db) + 1
    new_product = {
        "id": product_id,
        "created_at": datetime.now(),
        "updated_at": None,
        **product.dict()
    }
    products_db.append(new_product)
    return new_product

@app.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Get a product by ID",
    description="Retrieve detailed information about a specific product"
)
async def read_product(
    product_id: int = Path(..., title="The ID of the product to get", ge=1)
):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get(
    "/products/",
    response_model=PaginatedProducts,
    summary="List products",
    description="Get a paginated list of products with optional filtering"
)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price")
):
    # Apply filters
    filtered_products = products_db.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    # Calculate pagination
    total = len(filtered_products)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_products = filtered_products[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": paginated_products
    }

@app.put(
    "/products/{product_id}",
    response_model=Product,
    summary="Update a product",
    description="Update an existing product's information"
)
async def update_product(
    product_id: int,
    product_update: ProductBase,
    current_user: dict = Depends(get_current_user)
):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product
    product.update({
        **product_update.dict(),
        "updated_at": datetime.now()
    })
    
    return product

@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    description="Delete a product by ID"
)
async def delete_product(
    product_id: int,
    current_user: dict = Depends(get_current_user)
):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Remove product
    products_db.remove(product)
    
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This completes the FastAPI application for managing products. The code includes:

A Product model that extends ProductBase with ID and timestamp fields
A PaginatedProducts model for returning paginated results
CRUD endpoints for products:

POST to create products
GET to retrieve products (by ID or with pagination and filtering)
PUT to update products
DELETE to remove products


Authentication using OAuth2 (simplified for the example)
Comprehensive endpoint documentation using FastAPI's built-in features

The application uses an in-memory list for storage, which should be replaced with a proper database in a production environment.


## Inter-Process Communication

### ZeroMQ for IPC

Using ZeroMQ for inter-process communication:

```python
import zmq
import time
import json
import threading

# Basic patterns

# Request-Reply pattern
def server_rep():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    
    print("Server started, waiting for requests...")
    while True:
        message = socket.recv_json()
        print(f"Received request: {message}")
        
        # Process the message
        response = {"status": "success", "data": f"Processed {message['action']}"}
        
        # Send reply
        time.sleep(1)  # Simulate work
        socket.send_json(response)

def client_req():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    
    for i in range(5):
        request = {"action": f"action_{i}", "data": f"data_{i}"}
        print(f"Sending request: {request}")
        socket.send_json(request)
        
        # Wait for reply
        response = socket.recv_json()
        print(f"Received response: {response}")
        
        time.sleep(1)  # Wait before next request

# Publish-Subscribe pattern
def server_pub():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5556")
    
    print("Publisher started, broadcasting messages...")
    count = 0
    while True:
        topic = "updates"
        message = {"count": count, "time": time.time()}
        print(f"Publishing: {topic} {message}")
        socket.send_string(f"{topic} {json.dumps(message)}")
        count += 1
        time.sleep(1)

def client_sub(topics=None):
    if topics is None:
        topics = ["updates"]
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5556")
    
    for topic in topics:
        socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    print(f"Subscriber started, listening for topics: {topics}")
    while True:
        string = socket.recv_string()
        topic, message = string.split(' ', 1)
        data = json.loads(message)
        print(f"Received: {topic} {data}")
```

### Named Pipes

Using named pipes for IPC on Unix systems:

```python
import os
import time
import json
import threading

# Create named pipe
pipe_path = "/tmp/python_named_pipe"
if not os.path.exists(pipe_path):
    os.mkfifo(pipe_path)

# Writer process
def pipe_writer():
    print(f"Opening pipe for writing: {pipe_path}")
    with open(pipe_path, 'w') as pipe:
        for i in range(10):
            message = json.dumps({"count": i, "time": time.time()})
            print(f"Writing: {message}")
            pipe.write(message + '\n')
            pipe.flush()  # Ensure data is sent immediately
            time.sleep(1)

# Reader process
def pipe_reader():
    print(f"Opening pipe for reading: {pipe_path}")
    with open(pipe_path, 'r') as pipe:
        while True:
            message = pipe.readline()[:-1]  # Remove trailing newline
            if not message:
                print("Pipe closed")
                break
            data = json.loads(message)
            print(f"Read: {data}")

# Run reader and writer in separate threads
if __name__ == "__main__":
    reader_thread = threading.Thread(target=pipe_reader)
    reader_thread.daemon = True
    reader_thread.start()
    
    time.sleep(0.1)  # Give reader time to start
    pipe_writer()
```

### Shared Memory

Using shared memory with multiprocessing:

```python
import multiprocessing as mp
import numpy as np
import time

def worker(shared_array):
    """Worker process that modifies shared memory"""
    print(f"Worker process: Initial shared_array sum = {np.sum(shared_array)}")
    
    # Modify the shared array
    for i in range(shared_array.shape[0]):
        shared_array[i] = i * 2
    
    print(f"Worker process: Modified shared_array sum = {np.sum(shared_array)}")

def main():
    # Create shared memory array
    array_size = 10
    shared_array = mp.Array('d', array_size)  # 'd' is for double precision float
    
    # Initialize the array
    np_array = np.frombuffer(shared_array.get_obj())
    np_array[:] = np.arange(array_size)
    
    print(f"Main process: Initial shared_array sum = {np.sum(np_array)}")
    
    # Create and start worker process
    p = mp.Process(target=worker, args=(np_array,))
    p.start()
    p.join()
    
    # Check the array after worker process
    print(f"Main process: Final shared_array sum = {np.sum(np_array)}")

if __name__ == "__main__":
    main()
```

## Distributed Systems Patterns

### Service Discovery

Implementing service discovery with Consul:

```python
import consul
import requests
import json
import time
import uuid
import socket
from flask import Flask, jsonify

# Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

class ServiceRegistry:
    def __init__(self, service_name, service_port=None, consul_host='localhost', consul_port=8500):
        self.service_name = service_name
        self.service_id = f"{service_name}-{uuid.uuid4()}"
        self.consul_host = consul_host
        self.consul_port = consul_port
        
        # Get local IP
        self.ip = self._get_local_ip()
        self.port = service_port or self._find_free_port()
        
        # Connect to Consul
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        
        # Start health check endpoint
        if service_port:
            self._start_health_check_server()
    
    def _get_local_ip(self):
        """Get the local IP address"""
        try:
            # Create a socket to determine outgoing IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def _find_free_port(self):
        """Find a free port to use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _start_health_check_server(self):
        """Start Flask server for health checks in a separate thread"""
        import threading
        def run_app():
            app.run(host='0.0.0.0', port=self.port)
        
        threading.Thread(target=run_app, daemon=True).start()
        time.sleep(1)  # Give server time to start
    
    def register(self):
        """Register service with Consul"""
        service_address = self.ip
        service_port = self.port
        
        check = {
            "http": f"http://{service_address}:{service_port}/health",
            "interval": "10s",
            "timeout": "5s"
        }
        
        self.consul.agent.service.register(
            name=self.service_name,
            service_id=self.service_id,
            address=service_address,
            port=service_port,
            check=check
        )
        print(f"Registered service: {self.service_name} ({self.service_id}) at {service_address}:{service_port}")
        
        return {
            "name": self.service_name,
            "id": self.service_id,
            "address": service_address,
            "port": service_port
        }
    
    def deregister(self):
        """Deregister service from Consul"""
        self.consul.agent.service.deregister(self.service_id)
        print(f"Deregistered service: {self.service_name} ({self.service_id})")
    
    def discover_service(self, service_name):
        """Discover a service by name"""
        index, services = self.consul.catalog.service(service_name)
        
        if not services:
            return None
        
        # Return a random instance (for simple load balancing)
        import random
        service = random.choice(services)
        
        return {
            'id': service['ServiceID'],
            'name': service['ServiceName'],
            'address': service['ServiceAddress'] or service['Address'],
            'port': service['ServicePort'],
            'tags': service['ServiceTags']
        }
    
    def call_service(self, service_name, endpoint, method='GET', data=None):
        """Call another service"""
        service = self.discover_service(service_name)
        
        if not service:
            raise Exception(f"Service {service_name} not found")
        
        url = f"http://{service['address']}:{service['port']}/{endpoint.lstrip('/')}"
        print(f"Calling service: {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response.json() if response.text else None

# Example usage
if __name__ == "__main__":
    import atexit
    
    # Register a service
    registry = ServiceRegistry("example-service", service_port=8080)
    registry.register()
    
    # Ensure service is deregistered on exit
    atexit.register(registry.deregister)
    
    # Discover and call another service
    try:
        while True:
            try:
                # Try to discover a user service
                user_service = registry.discover_service("user-service")
                if user_service:
                    print(f"Found user service: {user_service}")
                    
                    # Try to call the service
                    try:
                        response = registry.call_service("user-service", "/api/users")
                        print(f"User service response: {response}")
                    except Exception as e:
                        print(f"Error calling user service: {e}")
                else:
                    print("User service not found")
            except Exception as e:
                print(f"Error discovering service: {e}")
            
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down...")
```

### Circuit Breaker

Implementing the Circuit Breaker pattern:

```python
import time
import logging
import functools
from enum import Enum

class CircuitState(Enum):
    CLOSED = 'CLOSED'       # Normal operation, calls allowed
    OPEN = 'OPEN'           # Circuit breaker is open, calls are blocked
    HALF_OPEN = 'HALF_OPEN' # Testing if service is available again

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30, 
                 expected_exceptions=(Exception,), name=None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions
        self.name = name or "default"
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        
        self.logger = logging.getLogger(f"circuit_breaker.{self.name}")
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self.logger.info(f"Circuit {self.name} state: HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                self.logger.warning(f"Circuit {self.name} is OPEN, rejecting call")
                raise CircuitBreakerOpenError(f"Circuit {self.name} is open")
        
        try:
            result = func(*args, **kwargs)
            
            # If successful and in half-open state, reset the circuit
            if self.state == CircuitState.HALF_OPEN:
                self.logger.info(f"Circuit {self.name} reset: HALF_OPEN -> CLOSED")
                self._reset()
            
            return result
        
        except self.expected_exceptions as e:
            # Handle expected exceptions (service failures)
            self._on_failure(e)
            raise
    
    def _on_failure(self, exception):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        self.logger.warning(
            f"Circuit {self.name} failure: {type(exception).__name__}, "
            f"count: {self.failure_count}/{self.failure_threshold}"
        )
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self.logger.error(f"Circuit {self.name} tripped: CLOSED -> OPEN")
            self.state = CircuitState.OPEN
        
        elif self.state == CircuitState.HALF_OPEN:
            self.logger.error(f"Circuit {self.name} reopened: HALF_OPEN -> OPEN")
            self.state = CircuitState.OPEN
    
    def _should_attempt_recovery(self):
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.recovery_timeout
    
    def _reset(self):
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

class CircuitBreakerOpenError(Exception):
    """Exception raised when a circuit breaker is open"""
    pass

# Example usage
import random
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)

@CircuitBreaker(failure_threshold=3, recovery_timeout=5)
def call_external_service():
    """Call a potentially failing external service"""
    # Simulate a service that sometimes fails
    if random.random() < 0.7:  # 70% chance of failure
        print("Service call failed!")
        raise requests.exceptions.RequestException("Service unavailable")
    
    print("Service call succeeded!")
    return "Service response data"

# Try calling the service repeatedly
def test_circuit_breaker():
    for i in range(20):
        print(f"\nAttempt {i+1}:")
        try:
            result = call_external_service()
            print(f"Result: {result}")
        except CircuitBreakerOpenError as e:
            print(f"Circuit breaker is open: {e}")
        except Exception as e:
            print(f"Service error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_circuit_breaker()
```

### Bulkhead Pattern

Implementing the Bulkhead pattern with thread pools:

```python
import concurrent.futures
import time
import random
import logging
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Bulkhead:
    """
    Bulkhead pattern implementation to isolate failures using thread pools.
    """
    
    def __init__(self, max_workers, name=None):
        self.name = name or "default"
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.logger = logging.getLogger(f"bulkhead.{self.name}")
        self.logger.info(f"Created bulkhead '{self.name}' with {max_workers} workers")
    
    def __call__(self, func):
        """Decorator for functions to be executed within this bulkhead."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                future = self.executor.submit(func, *args, **kwargs)
                return future.result()
            except concurrent.futures.TimeoutError:
                self.logger.error(f"Timeout executing {func.__name__} in bulkhead '{self.name}'")
                raise
            except Exception as e:
                self.logger.error(f"Error executing {func.__name__} in bulkhead '{self.name}': {e}")
                raise
        return wrapper
    
    def execute(self, func, *args, **kwargs):
        """Execute a function within this bulkhead."""
        return self.executor.submit(func, *args, **kwargs)
    
    def shutdown(self, wait=True):
        """Shutdown the bulkhead's thread pool."""
        self.logger.info(f"Shutting down bulkhead '{self.name}'")
        self.executor.shutdown(wait=wait)

# Create bulkheads for different services
database_bulkhead = Bulkhead(max_workers=5, name="database")
api_bulkhead = Bulkhead(max_workers=10, name="api")
reporting_bulkhead = Bulkhead(max_workers=2, name="reporting")

# Example service functions
@database_bulkhead
def database_query(query_id):
    """Simulate a database query."""
    logger.info(f"Executing database query {query_id}")
    # Simulate query execution time
    time.sleep(random.uniform(0.1, 0.5))
    # Simulate occasional failure
    if random.random() < 0.2:
        logger.error(f"Database query {query_id} failed")
        raise Exception(f"Database query {query_id} failed")
    logger.info(f"Database query {query_id} completed")
    return f"Result of query {query_id}"

@api_bulkhead
def api_request(request_id):
    """Simulate an API request."""
    logger.info(f"Processing API request {request_id}")
    # Simulate request processing time
    time.sleep(random.uniform(0.2, 1.0))
    # Simulate occasional failure
    if random.random() < 0.1:
        logger.error(f"API request {request_id} failed")
        raise Exception(f"API request {request_id} failed")
    logger.info(f"API request {request_id} completed")
    return f"Response for request {request_id}"

@reporting_bulkhead
def generate_report(report_id):
    """Simulate a resource-intensive report generation."""
    logger.info(f"Generating report {report_id}")
    # Simulate report generation time (longer operation)
    time.sleep(random.uniform(2.0, 5.0))
    logger.info(f"Report {report_id} generated")
    return f"Report {report_id} data"

# Example of using the bulkhead pattern
def run_simulation():
    """Run a simulation of different service calls with bulkheads."""
    
    # Submit multiple concurrent tasks
    futures = []
    
    # Database queries
    for i in range(10):
        futures.append(database_bulkhead.execute(database_query, i))
    
    # API requests
    for i in range(15):
        futures.append(api_bulkhead.execute(api_request, i))
    
    # Reports (resource-intensive)
    for i in range(5):
        futures.append(reporting_bulkhead.execute(generate_report, i))
    
    # Wait for all futures to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            result = future.result()
            logger.info(f"Task completed: {result}")
        except Exception as e:
            logger.error(f"Task failed: {e}")
    
    # Shutdown bulkheads
    database_bulkhead.shutdown()
    api_bulkhead.shutdown()
    reporting_bulkhead.shutdown()

if __name__ == "__main__":
    run_simulation()
```

### Retry Pattern

Implementing a retry mechanism with exponential backoff:

```python
import time
import random
import logging
import functools
from typing import Callable, Type, Tuple, Optional, Union, List

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetryableError(Exception):
    """Base class for errors that can be retried."""
    pass

def retry(
    max_attempts: int = 3,
    retry_exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = (RetryableError,),
    backoff_factor: float = 0.5,
    max_backoff: float = 30.0,
    jitter: bool = True
) -> Callable:
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts.
        retry_exceptions: Exception types that trigger a retry.
        backoff_factor: Factor to determine the exponential backoff delay.
        max_backoff: Maximum backoff delay in seconds.
        jitter: Whether to add randomness to backoff delay.
    
    Returns:
        Decorated function that will be retried on specified exceptions.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    if attempt > 1:
                        # Calculate backoff delay
                        backoff = min(backoff_factor * (2 ** (attempt - 1)), max_backoff)
                        
                        # Add jitter if enabled
                        if jitter:
                            backoff = random.uniform(0.5 * backoff, 1.5 * backoff)
                        
                        logger.info(f"Retry attempt {attempt}/{max_attempts} for {func.__name__} "
                                   f"after {backoff:.2f}s delay")
                        time.sleep(backoff)
                    
                    return func(*args, **kwargs)
                
                except retry_exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt}/{max_attempts} for {func.__name__} "
                                  f"failed: {type(e).__name__}: {str(e)}")
                    
                    # Raise exception if this was the last attempt
                    if attempt == max_attempts:
                        logger.error(f"All {max_attempts} retry attempts for {func.__name__} failed")
                        raise last_exception
            
            # This should never be reached, but added for completeness
            raise last_exception
        
        return wrapper
    
    return decorator

# Example usage with simulated HTTP requests
def simulate_http_request(endpoint: str, data: Optional[dict] = None) -> dict:
    """Simulate an HTTP request that might fail."""
    logger.info(f"Making HTTP request to {endpoint}")
    
    # Simulate network errors
    error_chance = random.random()
    
    if error_chance < 0.4:  # 40% chance of connection error
        logger.error(f"Connection error to {endpoint}")
        raise RetryableError("Connection refused")
    
    elif error_chance < 0.6:  # 20% chance of timeout
        logger.error(f"Request timeout to {endpoint}")
        raise RetryableError("Request timed out")
    
    elif error_chance < 0.7:  # 10% chance of server error
        logger.error(f"Server error from {endpoint}")
        raise RetryableError("Internal server error")
    
    # Success case
    logger.info(f"Request to {endpoint} succeeded")
    return {"status": "success", "data": "Response data"}

# Apply retry decorator to the simulated HTTP request
@retry(max_attempts=5, backoff_factor=1.0, jitter=True)
def make_request_with_retry(endpoint: str, data: Optional[dict] = None) -> dict:
    return simulate_http_request(endpoint, data)

# Test the retry mechanism
def test_retry():
    try:
        result = make_request_with_retry("https://api.example.com/data", {"key": "value"})
        logger.info(f"Request successful: {result}")
    except Exception as e:
        logger.error(f"Request failed after retries: {e}")

if __name__ == "__main__":
    test_retry()
```


## Event-Driven Architecture

### Event Publishing/Subscribing

Using RabbitMQ for event-driven architecture:

```python
import pika
import json
import uuid
import threading
import time
import logging
from typing import Dict, Any, Callable, List

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventBus:
    """
    Event bus implementation using RabbitMQ.
    
    Provides publish-subscribe messaging for event-driven architecture.
    """
    
    def __init__(self, 
                 host: str = 'localhost', 
                 port: int = 5672, 
                 vhost: str = '/',
                 username: str = 'guest', 
                 password: str = 'guest',
                 exchange_name: str = 'events'):
        self.host = host
        self.port = port
        self.vhost = vhost
        self.username = username
        self.password = password
        self.exchange_name = exchange_name
        
        # Store connection and channel
        self.connection = None
        self.channel = None
        
        # Store subscriber callbacks
        self.subscribers: Dict[str, List[Callable]] = {}
        
        # Connect to RabbitMQ
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ."""
        try:
            # Connection parameters
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=pika.PlainCredentials(self.username, self.password),
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Create connection and channel
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True,
                auto_delete=False
            )
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}/{self.vhost}")
        
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish(self, event_type: str, event_data: Dict[str, Any], headers: Dict[str, str] = None):
        """
        Publish an event to the event bus.
        
        Args:
            event_type: Type of the event (routing key).
            event_data: Data payload for the event.
            headers: Optional message headers.
        """
        if not self.connection or self.connection.is_closed:
            self._connect()
        
        # Create the event message
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": int(time.time()),
            "data": event_data
        }
        
        # Serialize the event
        event_json = json.dumps(event)
        
        # Set up message properties
        properties = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2,  # Persistent
            headers=headers
        )
        
        try:
            # Publish the event
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=event_type,
                body=event_json,
                properties=properties
            )
            
            logger.info(f"Published event: {event_type} ({event['id']})")
        
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            # Try to reconnect
            self._connect()
            raise
    
    def subscribe(self, event_types: List[str], callback: Callable, queue_name: str = None):
        """
        Subscribe to events of specified types.
        
        Args:
            event_types: Types of events to subscribe to (routing keys).
            callback: Function to call when an event is received.
            queue_name: Optional name for the queue. If None, a random name is generated.
        
        Returns:
            Queue name that was created or used.
        """
        if not self.connection or self.connection.is_closed:
            self._connect()
        
        # Generate queue name if not provided
        if queue_name is None:
            queue_name = f"queue-{str(uuid.uuid4())}"
        
        # Declare the queue
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False
        )
        
        # Bind the queue to the exchange for each event type
        for event_type in event_types:
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=queue_name,
                routing_key=event_type
            )
            
            # Store the callback
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)
            
            logger.info(f"Subscribed to event type: {event_type} on queue: {queue_name}")
        
        # Set up the consumer
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: self._on_message(
                ch, method, properties, body, callback
            ),
            auto_ack=False
        )
        
        # Start consuming in a separate thread
        thread = threading.Thread(target=self._start_consuming)
        thread.daemon = True
        thread.start()
        
        return queue_name
    
    def _on_message(self, ch, method, properties, body, callback):
        """Handle received messages."""
        try:
            # Parse the event
            event = json.loads(body)
            
            logger.info(f"Received event: {event['type']} ({event['id']})")
            
            # Call the callback with the event
            callback(event)
            
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            # Negative acknowledgment, requeue the message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def _start_consuming(self):
        """Start consuming messages."""
        try:
            logger.info("Started consuming events")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming events: {e}")
            # Try to reconnect
            self._connect()
    
    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.channel.stop_consuming()
            self.connection.close()
            logger.info("Connection to RabbitMQ closed")

# Example usage with a user service that publishes and subscribes to events
class UserService:
    """
    Example service that publishes and subscribes to user-related events.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.users = {}  # Simple in-memory storage
        
        # Subscribe to events
        self.event_bus.subscribe(
            event_types=["user.created", "user.updated", "user.deleted"],
            callback=self.handle_user_event,
            queue_name="user_service_queue"
        )
    
    def handle_user_event(self, event):
        """Handle user events."""
        event_type = event["type"]
        user_data = event["data"]
        
        if event_type == "user.created":
            logger.info(f"Processing user creation: {user_data['id']}")
            # Update local cache
            self.users[user_data['id']] = user_data
        
        elif event_type == "user.updated":
            logger.info(f"Processing user update: {user_data['id']}")
            # Update local cache
            if user_data['id'] in self.users:
                self.users[user_data['id']].update(user_data)
        
        elif event_type == "user.deleted":
            logger.info(f"Processing user deletion: {user_data['id']}")
            # Remove from local cache
            if user_data['id'] in self.users:
                del self.users[user_data['id']]
    
    def create_user(self, user_id, name, email):
        """Create a new user and publish an event."""
        user = {
            "id": user_id,
            "name": name,
            "email": email,
            "created_at": int(time.time())
        }
        
        # Store the user
        self.users[user_id] = user
        
        # Publish the event
        self.event_bus.publish(
            event_type="user.created",
            event_data=user
        )
        
        return user_id
    
    def update_user(self, user_id, **updates):
        """Update a user and publish an event."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        # Update the user
        user = self.users[user_id]
        user.update(updates)
        user["updated_at"] = int(time.time())
        
        # Publish the event
        self.event_bus.publish(
            event_type="user.updated",
            event_data=user
        )
        
        return user
    
    def delete_user(self, user_id):
        """Delete a user and publish an event."""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        # Delete the user
        user = self.users.pop(user_id)
        
        # Publish the event
        self.event_bus.publish(
            event_type="user.deleted",
            event_data={"id": user_id}
        )
        
        return user
```

### Event Sourcing

Implementing event sourcing pattern:
```python
import json
import uuid
import time
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

# Event store interface
class EventStore(ABC):
    @abstractmethod
    def append_events(self, aggregate_id: str, events: List[Dict[str, Any]], expected_version: int) -> int:
        pass
    
    @abstractmethod
    def get_events(self, aggregate_id: str) -> List[Dict[str, Any]]:
        pass

# Simple in-memory event store implementation
class InMemoryEventStore(EventStore):
    def __init__(self):
        self.events: Dict[str, List[Dict[str, Any]]] = {}
    
    def append_events(self, aggregate_id: str, events: List[Dict[str, Any]], expected_version: int) -> int:
        """
        Append events to the store for a specific aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
            events: List of events to append
            expected_version: Expected current version of the aggregate
        
        Returns:
            New version of the aggregate
        
        Raises:
            ConcurrencyError: If the actual version doesn't match the expected version
        """
        # Initialize events list if not exists
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
        
        # Check for concurrency issues
        current_version = len(self.events[aggregate_id])
        if expected_version != current_version:
            raise ConcurrencyError(
                f"Concurrency error for aggregate {aggregate_id}: "
                f"Expected version {expected_version}, but got {current_version}"
            )
        
        # Append events
        self.events[aggregate_id].extend(events)
        
        # Return new version
        return len(self.events[aggregate_id])
    
    def get_events(self, aggregate_id: str) -> List[Dict[str, Any]]:
        """
        Get all events for a specific aggregate.
        
        Args:
            aggregate_id: ID of the aggregate
        
        Returns:
            List of events
        """
        return self.events.get(aggregate_id, [])

# Custom exception for concurrency issues
class ConcurrencyError(Exception):
    pass

# Base aggregate class
class Aggregate:
    def __init__(self, id: str = None):
        self.id = id or str(uuid.uuid4())
        self.version = 0
        self.changes: List[Dict[str, Any]] = []
    
    def apply_event(self, event: Dict[str, Any]):
        """
        Apply an event to the aggregate.
        
        Args:
            event: Event to apply
        """
        # Determine the event handler method
        event_type = event["type"]
        handler_name = f"apply_{event_type}"
        
        # Check if handler exists
        if not hasattr(self, handler_name):
            raise ValueError(f"No handler found for event type: {event_type}")
        
        # Call the handler
        handler = getattr(self, handler_name)
        handler(event["data"])
        
        # Increment version
        self.version += 1
    
    def apply_changes(self, events: List[Dict[str, Any]]):
        """
        Apply multiple events to the aggregate.
        
        Args:
            events: List of events to apply
        """
        for event in events:
            self.apply_event(event)
    
    def commit_changes(self, event_store: EventStore):
        """
        Commit changes to the event store.
        
        Args:
            event_store: Event store to commit to
        
        Returns:
            Number of committed events
        """
        if not self.changes:
            return 0
        
        # Append events to the store
        self.version = event_store.append_events(
            self.id,
            self.changes,
            self.version
        )
        
        # Clear changes
        count = len(self.changes)
        self.changes = []
        
        return count
    
    def add_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Add a new event to the changes list.
        
        Args:
            event_type: Type of the event
            event_data: Event data
        """
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": int(time.time()),
            "data": event_data
        }
        
        # Apply the event
        self.apply_event(event)
        
        # Add to changes
        self.changes.append(event)

# Example user aggregate
class User(Aggregate):
    def __init__(self, id: str = None):
        super().__init__(id)
        self.name = None
        self.email = None
        self.created_at = None
        self.updated_at = None
        self.active = False
    
    @staticmethod
    def create(name: str, email: str) -> 'User':
        """
        Create a new user.
        
        Args:
            name: User name
            email: User email
        
        Returns:
            New User instance
        """
        user = User()
        user.add_event("user_created", {
            "name": name,
            "email": email
        })
        return user
    
    def update_name(self, name: str):
        """Update user name."""
        self.add_event("user_name_updated", {
            "name": name
        })
    
    def update_email(self, email: str):
        """Update user email."""
        self.add_event("user_email_updated", {
            "email": email
        })
    
    def deactivate(self):
        """Deactivate the user."""
        if not self.active:
            return  # Already inactive
        
        self.add_event("user_deactivated", {})
    
    def activate(self):
        """Activate the user."""
        if self.active:
            return  # Already active
        
        self.add_event("user_activated", {})
    
    # Event handlers
    def apply_user_created(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.email = data["email"]
        self.created_at = int(time.time())
        self.active = True
    
    def apply_user_name_updated(self, data: Dict[str, Any]):
        self.name = data["name"]
        self.updated_at = int(time.time())
    
    def apply_user_email_updated(self, data: Dict[str, Any]):
        self.email = data["email"]
        self.updated_at = int(time.time())
    
    def apply_user_deactivated(self, data: Dict[str, Any]):
        self.active = False
        self.updated_at = int(time.time())
    
    def apply_user_activated(self, data: Dict[str, Any]):
        self.active = True
        self.updated_at = int(time.time())

# User repository
class UserRepository:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    def save(self, user: User):
        """
        Save user changes to the event store.
        
        Args:
            user: User to save
        """
        user.commit_changes(self.event_store)
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID
        
        Returns:
            User instance or None if not found
        """
        # Get events from the store
        events = self.event_store.get_events(user_id)
        
        if not events:
            return None
        
        # Create user and apply events
        user = User(user_id)
        user.apply_changes(events)
        
        return user

# Example usage
def run_event_sourcing_example():
    # Create event store
    event_store = InMemoryEventStore()
    
    # Create user repository
    user_repo = UserRepository(event_store)
    
    # Create a new user
    user = User.create("John Doe", "john@example.com")
    user_repo.save(user)
    print(f"Created user: {user.id} - {user.name} ({user.email})")
    
    # Retrieve the user
    retrieved_user = user_repo.get_by_id(user.id)
    print(f"Retrieved user: {retrieved_user.id} - {retrieved_user.name} ({retrieved_user.email})")
    
    # Update the user
    retrieved_user.update_name("John Updated")
    retrieved_user.update_email("john.updated@example.com")
    user_repo.save(retrieved_user)
    print(f"Updated user: {retrieved_user.id} - {retrieved_user.name} ({retrieved_user.email})")
    
    # Deactivate the user
    retrieved_user.deactivate()
    user_repo.save(retrieved_user)
    print(f"Deactivated user: {retrieved_user.id} - Active: {retrieved_user.active}")
    
    # Get all events for the user
    events = event_store.get_events(user.id)
    print(f"Event history for user {user.id}:")
    for i, event in enumerate(events):
        print(f"  {i+1}. {event['type']} at {event['timestamp']}")
```

### CQRS Pattern

Implementing Command Query Responsibility Segregation:
```python
import uuid
import time
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
import threading
import json

# Command and Query interfaces
class Command:
    """Base class for commands."""
    pass

class Query:
    """Base class for queries."""
    pass

# Handler interfaces
class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command):
        pass

class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> Any:
        pass

# Event bus for publishing domain events
class EventBus:
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
    
    def publish(self, event_type: str, event_data: Dict[str, Any]):
        """Publish an event to all registered handlers."""
        if event_type not in self.handlers:
            return
        
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": int(time.time()),
            "data": event_data
        }
        
        for handler in self.handlers[event_type]:
            handler(event)
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of a specific type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)

# Command and Query buses
class CommandBus:
    def __init__(self):
        self.handlers: Dict[type, CommandHandler] = {}
    
    def register(self, command_type: type, handler: CommandHandler):
        """Register a handler for a command type."""
        self.handlers[command_type] = handler
    
    def dispatch(self, command: Command):
        """Dispatch a command to its handler."""
        handler = self.handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for command type: {type(command).__name__}")
        
        return handler.handle(command)

class QueryBus:
    def __init__(self):
        self.handlers: Dict[type, QueryHandler] = {}
    
    def register(self, query_type: type, handler: QueryHandler):
        """Register a handler for a query type."""
        self.handlers[query_type] = handler
    
    def dispatch(self, query: Query) -> Any:
        """Dispatch a query to its handler."""
        handler = self.handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for query type: {type(query).__name__}")
        
        return handler.handle(query)

# User domain model, commands, and events
class User:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
        self.active = True
        self.created_at = int(time.time())
        self.updated_at = None

# User commands
class CreateUserCommand(Command):
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class UpdateUserCommand(Command):
    def __init__(self, id: str, name: str = None, email: str = None):
        self.id = id
        self.name = name
        self.email = email

class DeactivateUserCommand(Command):
    def __init__(self, id: str):
        self.id = id

# User queries
class GetUserByIdQuery(Query):
    def __init__(self, id: str):
        self.id = id

class GetAllUsersQuery(Query):
    pass

class GetActiveUsersQuery(Query):
    pass

# Read models and repositories
class UserReadModel:
    def __init__(self, id: str, name: str, email: str, active: bool = True, 
                 created_at: int = None, updated_at: int = None):
        self.id = id
        self.name = name
        self.email = email
        self.active = active
        self.created_at = created_at or int(time.time())
        self.updated_at = updated_at

class UserWriteRepository:
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def save(self, user: User):
        self.users[user.id] = user
    
    def get_by_id(self, id: str) -> Optional[User]:
        return self.users.get(id)
    
    def delete(self, id: str):
        if id in self.users:
            del self.users[id]

class UserReadRepository:
    def __init__(self):
        self.users: Dict[str, UserReadModel] = {}
    
    def save(self, user: UserReadModel):
        self.users[user.id] = user
    
    def get_by_id(self, id: str) -> Optional[UserReadModel]:
        return self.users.get(id)
    
    def get_all(self) -> List[UserReadModel]:
        return list(self.users.values())
    
    def get_active(self) -> List[UserReadModel]:
        return [user for user in self.users.values() if user.active]

# Command handlers
class CreateUserCommandHandler(CommandHandler):
    def __init__(self, write_repo: UserWriteRepository, event_bus: EventBus):
        self.write_repo = write_repo
        self.event_bus = event_bus
    
    def handle(self, command: CreateUserCommand):
        # Create a new user
        user_id = str(uuid.uuid4())
        user = User(user_id, command.name, command.email)
        
        # Save to write repository
        self.write_repo.save(user)
        
        # Publish event
        self.event_bus.publish("user_created", {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "active": user.active,
            "created_at": user.created_at
        })
        
        return user.id

class UpdateUserCommandHandler(CommandHandler):
    def __init__(self, write_repo: UserWriteRepository, event_bus: EventBus):
        self.write_repo = write_repo
        self.event_bus = event_bus
    
    def handle(self, command: UpdateUserCommand):
        # Get the user
        user = self.write_repo.get_by_id(command.id)
        if not user:
            raise ValueError(f"User not found: {command.id}")
        
        # Update fields
        updated = False
        if command.name is not None and command.name != user.name:
            user.name = command.name
            updated = True
        
        if command.email is not None and command.email != user.email:
            user.email = command.email
            updated = True
        
        if updated:
            user.updated_at = int(time.time())
            
            # Save to write repository
            self.write_repo.save(user)
            
            # Publish event
            self.event_bus.publish("user_updated", {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "updated_at": user.updated_at
            })

class DeactivateUserCommandHandler(CommandHandler):
    def __init__(self, write_repo: UserWriteRepository, event_bus: EventBus):
        self.write_repo = write_repo
        self.event_bus = event_bus
    
    def handle(self, command: DeactivateUserCommand):
        # Get the user
        user = self.write_repo.get_by_id(command.id)
        if not user:
            raise ValueError(f"User not found: {command.id}")
        
        if not user.active:
            return  # Already inactive
        
        # Deactivate the user
        user.active = False
        user.updated_at = int(time.time())
        
        # Save to write repository
        self.write_repo.save(user)
        
        # Publish event
        self.event_bus.publish("user_deactivated", {
            "id": user.id,
            "updated_at": user.updated_at
        })

# Query handlers
class GetUserByIdQueryHandler(QueryHandler):
    def __init__(self, read_repo: UserReadRepository):
        self.read_repo = read_repo
    
    def handle(self, query: GetUserByIdQuery) -> Optional[UserReadModel]:
        return self.read_repo.get_by_id(query.id)

class GetAllUsersQueryHandler(QueryHandler):
    def __init__(self, read_repo: UserReadRepository):
        self.read_repo = read_repo
    
    def handle(self, query: GetAllUsersQuery) -> List[UserReadModel]:
        return self.read_repo.get_all()

class GetActiveUsersQueryHandler(QueryHandler):
    def __init__(self, read_repo: UserReadRepository):
        self.read_repo = read_repo
    
    def handle(self, query: GetActiveUsersQuery) -> List[UserReadModel]:
        return self.read_repo.get_active()

# Event handlers to update read models
class UserEventHandler:
    def __init__(self, read_repo: UserReadRepository):
        self.read_repo = read_repo
    
    def handle_user_created(self, event: Dict[str, Any]):
        data = event["data"]
        user = UserReadModel(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            active=data["active"],
            created_at=data["created_at"]
        )
        self.read_repo.save(user)
    
    def handle_user_updated(self, event: Dict[str, Any]):
        data = event["data"]
        user = self.read_repo.get_by_id(data["id"])
        if not user:
            return
        
        user.name = data["name"]
        user.email = data["email"]
        user.updated_at = data["updated_at"]
        self.read_repo.save(user)
    
    def handle_user_deactivated(self, event: Dict[str, Any]):
        data = event["data"]
        user = self.read_repo.get_by_id(data["id"])
        if not user:
            return
        
        user.active = False
        user.updated_at = data["updated_at"]
        self.read_repo.save(user)

# Main application setup
class UserApplication:
    def __init__(self):
        # Create buses
        self.event_bus = EventBus()
        self.command_bus = CommandBus()
        self.query_bus = QueryBus()
        
        # Create repositories
        self.write_repo = UserWriteRepository()
        self.read_repo = UserReadRepository()
        
        # Register command handlers
        self.command_bus.register(
            CreateUserCommand,
            CreateUserCommandHandler(self.write_repo, self.event_bus)
        )
        self.command_bus.register(
            UpdateUserCommand,
            UpdateUserCommandHandler(self.write_repo, self.event_bus)
        )
        self.command_bus.register(
            DeactivateUserCommand,
            DeactivateUserCommandHandler(self.write_repo, self.event_bus)
        )
        
        # Register query handlers
        self.query_bus.register(
            GetUserByIdQuery,
            GetUserByIdQueryHandler(self.read_repo)
        )
        self.query_bus.register(
            GetAllUsersQuery,
            GetAllUsersQueryHandler(self.read_repo)
        )
        self.query_bus.register(
            GetActiveUsersQuery,
            GetActiveUsersQueryHandler(self.read_repo)
        )
        
        # Register event handlers
        event_handler = UserEventHandler(self.read_repo)
        self.event_bus.subscribe("user_created", event_handler.handle_user_created)
        self.event_bus.subscribe("user_updated", event_handler.handle_user_updated)
        self.event_bus.subscribe("user_updated", event_handler.handle_user_updated)
        self.event_bus.subscribe("user_deactivated", event_handler.handle_user_deactivated)
    
    def create_user(self, name: str, email: str) -> str:
        """Create a new user."""
        return self.command_bus.dispatch(CreateUserCommand(name, email))
    
    def update_user(self, id: str, name: str = None, email: str = None):
        """Update a user."""
        self.command_bus.dispatch(UpdateUserCommand(id, name, email))
    
    def deactivate_user(self, id: str):
        """Deactivate a user."""
        self.command_bus.dispatch(DeactivateUserCommand(id))
    
    def get_user(self, id: str) -> Optional[UserReadModel]:
        """Get a user by ID."""
        return self.query_bus.dispatch(GetUserByIdQuery(id))
    
    def get_all_users(self) -> List[UserReadModel]:
        """Get all users."""
        return self.query_bus.dispatch(GetAllUsersQuery())
    
    def get_active_users(self) -> List[UserReadModel]:
        """Get active users."""
        return self.query_bus.dispatch(GetActiveUsersQuery())

    # Example usage
    def run_cqrs_example():
    # Create application
    app = UserApplication()
    
    # Create users
    user1_id = app.create_user("John Doe", "john@example.com")
    user2_id = app.create_user("Jane Smith", "jane@example.com")
    
    # Display users
    print("All users:")
    for user in app.get_all_users():
        print(f"  - {user.id}: {user.name} ({user.email})")
    
    # Update a user
    app.update_user(user1_id, name="John Updated")
    
    # Get and display the updated user
    user = app.get_user(user1_id)
    print(f"\nUpdated user: {user.id} - {user.name} ({user.email})")
    
    # Deactivate a user
    app.deactivate_user(user2_id)
    
    # Display active users
    print("\nActive users:")
    for user in app.get_active_users():
        print(f"  - {user.id}: {user.name} ({user.email})")
```

## Integration Testing

### Testing Microservices

```python
import pytest
import requests
import time

# Test API endpoints across services
def test_end_to_end_flow():
    # Create a user
    user_response = requests.post(
        "http://user-service:8000/api/users",
        json={"name": "Test User", "email": "test@example.com"}
    )
    assert user_response.status_code == 201
    user_id = user_response.json()["id"]
    
    # Create an order for the user
    order_response = requests.post(
        "http://order-service:8001/api/orders",
        json={"user_id": user_id, "items": [{"product_id": "123", "quantity": 2}]}
    )
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    
    # Verify order status
    status_response = requests.get(f"http://order-service:8001/api/orders/{order_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "created"
```

### Testing Message Queues

```python
import pika
import json
import threading
import queue
import time

def test_message_publishing_and_receiving():
    # Setup RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    
    # Declare queue
    test_queue = "test_queue"
    channel.queue_declare(queue=test_queue, durable=False, auto_delete=True)
    
    # Setup message collector
    received_messages = queue.Queue()
    
    # Define callback
    def callback(ch, method, properties, body):
        received_messages.put(json.loads(body))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # Start consuming
    channel.basic_consume(queue=test_queue, on_message_callback=callback)
    
    # Start consumer thread
    consumer_thread = threading.Thread(
        target=lambda: channel.start_consuming()
    )
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Publish test message
    test_message = {"key": "value", "timestamp": time.time()}
    channel.basic_publish(
        exchange="",
        routing_key=test_queue,
        body=json.dumps(test_message)
    )
    
    # Wait for message to be processed
    try:
        received = received_messages.get(timeout=5)
        assert received["key"] == test_message["key"]
    finally:
        channel.stop_consuming()
        connection.close()
```

### Monitoring and Observability
#### Prometheus Metrics
```python
from flask import Flask, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest

app = Flask(__name__)

# Define metrics
REQUEST_COUNT = Counter('app_request_count', 'App Request Count', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency', ['endpoint'])
ACTIVE_REQUESTS = Gauge('app_active_requests', 'Active requests')

@app.before_request
def before_request():
    ACTIVE_REQUESTS.inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    
    # Record request latency
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.endpoint).observe(latency)
    
    # Count requests
    REQUEST_COUNT.labels(request.method, request.endpoint, response.status_code).inc()
    
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

#### Distributed Tracing
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "my-service"})
    )
)

# Set up Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

# Add exporter to provider
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Get tracer
tracer = trace.get_tracer(__name__)

# Use tracing in functions
def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        
        # Process the order...
        result = {"status": "processed"}
        
        return result
```

#### Centralized Logging
```python
import logging
import json
from pythonjsonlogger import jsonlogger

# Configure JSON logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use structured logging
def create_user(name, email):
    logger.info("Creating user", extra={
        "user_name": name,
        "user_email": email,
        "operation": "create_user"
    })
    
    # Create user logic...
    user_id = "123456"
    
    logger.info("User created successfully", extra={
        "user_id": user_id,
        "user_name": name,
        "operation": "create_user"
    })
    
    return user_id
```

### Best Practices
#### Loose Coupling
Design systems to minimize dependencies:

- Use message queues for asynchronous communication
- Define clear service boundaries
- Implement contracts/interfaces between services
- Avoid shared databases

### Error Handling

Implement robust error handling:
```python
def call_service(retry_count=3, backoff=1):
    for attempt in range(retry_count):
        try:
            return requests.get("http://service/endpoint", timeout=5)
        except requests.RequestException as e:
            if attempt == retry_count - 1:
                raise
            time.sleep(backoff * (2 ** attempt))  # Exponential backoff
```

### Documentation

Document integration points:
```python
class OrderClient:
    """
    Client for Order Service API.
    
    Endpoints:
    - GET /orders/{id} - Get order details
    - POST /orders - Create a new order
    
    Authentication: Bearer token required in Authorization header
    """
```

### Security
Secure service-to-service communication:

- Use mutual TLS authentication
- Implement API keys or JWT tokens
- Set up proper network segmentation
- Apply the principle of least privilege
- Regularly audit and rotate credentials