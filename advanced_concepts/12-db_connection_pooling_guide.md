# Database Connection Pooling: Junior to Senior Developer Guide

*A comprehensive guide for Python developers using PostgreSQL and FastAPI*

---

## Table of Contents

1. [Understanding Connection Pooling](#understanding-connection-pooling)
2. [The Problem Without Pooling](#the-problem-without-pooling)
3. [How Connection Pooling Works](#how-connection-pooling-works)
4. [Pool Sizing and Configuration](#pool-sizing-and-configuration)
5. [Implementation in FastAPI with PostgreSQL](#implementation-in-fastapi-with-postgresql)
6. [Pool Lifecycle Management](#pool-lifecycle-management)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)
9. [Advanced Topics](#advanced-topics)
10. [Real-World Case Studies](#real-world-case-studies)
11. [Best Practices Checklist](#best-practices-checklist)

---

## Understanding Connection Pooling

### What is Database Connection Pooling?

Database connection pooling is like managing a **company car fleet** instead of having employees rent cars every time they need transportation.

**Without Pooling (Car Rental Model):**
- Every database query requires creating a new connection
- Each connection setup involves authentication, SSL handshake, and resource allocation
- After the query, the connection is closed and resources are freed
- This is like filling out rental paperwork every time you need a car

**With Pooling (Company Fleet Model):**
- A pool of pre-established connections is maintained
- Applications borrow connections from the pool when needed
- Connections are returned to the pool after use, not closed
- This is like checking out a company car with just your employee ID

### Why Connection Pooling Matters

**Performance Impact:**
```python
# Without pooling - each request
connection_setup_time = 100ms  # Authentication, SSL, handshake
query_execution_time = 5ms     # Actual query
connection_teardown_time = 10ms # Cleanup
total_time_per_request = 115ms

# With pooling - each request
connection_checkout_time = 0.1ms # Get from pool
query_execution_time = 5ms       # Same query
connection_return_time = 0.1ms   # Return to pool
total_time_per_request = 5.2ms   # 22x faster!
```

**Resource Management:**
- PostgreSQL default max_connections = 100-200
- Each connection uses ~8MB of RAM
- Without pooling: 1000 users = potential 1000 connections = server crash
- With pooling: 1000 users share 20 connections = stable performance

---

## The Problem Without Pooling

### E-commerce Example: Product Page Load

```python
# BAD: No connection pooling
import asyncpg
from fastapi import FastAPI

app = FastAPI()

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    # Create new connection for each request
    conn = await asyncpg.connect("postgresql://user:pass@localhost/ecommerce")
    
    try:
        # Get product details
        product = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", product_id
        )
        
        # Get product reviews
        reviews = await conn.fetch(
            "SELECT * FROM reviews WHERE product_id = $1 LIMIT 5", product_id
        )
        
        # Get related products
        related = await conn.fetch(
            "SELECT * FROM products WHERE category_id = $1 LIMIT 4", 
            product.category_id
        )
        
        return {
            "product": dict(product),
            "reviews": [dict(r) for r in reviews],
            "related": [dict(r) for r in related]
        }
    finally:
        await conn.close()  # Close connection every time
```

**Problems with this approach:**
- Each page load creates a new connection (100ms overhead)
- Under load, database runs out of connections
- High latency due to connection setup time
- Database server CPU wasted on connection management

### Load Testing Results

```bash
# Load test: 100 concurrent users
# Without pooling:
# - Average response time: 400ms
# - Database connections: 100+ (hitting limits)
# - CPU usage: 80% (connection overhead)
# - Memory usage: 800MB (100 connections × 8MB)

# With pooling (pool_size=10):
# - Average response time: 50ms  
# - Database connections: 10 (stable)
# - CPU usage: 20% (mostly query processing)
# - Memory usage: 80MB (10 connections × 8MB)
```

---

## How Connection Pooling Works

### The Pool Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Server                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Connection Pool                       │   │
│  │                                                      │   │
│  │  [conn1] [conn2] [conn3] [conn4] [conn5]           │   │
│  │    ↓       ↓       ↓       ↓       ↓               │   │
│  │    Available    In Use   Available  In Use         │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                 │
└───────────────────────────┼─────────────────────────────────┘
                            ↓
                  ┌─────────────────────┐
                  │   PostgreSQL DB     │
                  │                     │
                  │  max_connections    │
                  │        = 100        │
                  └─────────────────────┘
```

### Pool Operations Flow

**Getting a Connection:**
```python
async def get_connection_flow():
    # 1. Check if pool has available connections
    if pool.has_available_connection():
        conn = pool.get_available()  # ~0.1ms
        return conn
    
    # 2. If pool not full, create new connection
    elif pool.current_size < pool.max_size:
        conn = await create_new_connection()  # ~100ms (one-time cost)
        pool.add_to_pool(conn)
        return conn
    
    # 3. If pool full, wait for available connection
    else:
        conn = await pool.wait_for_available()  # Wait time varies
        return conn
```

**Returning a Connection:**
```python
async def return_connection_flow(conn):
    # 1. Check if connection is still healthy
    if await conn.is_alive():
        pool.mark_as_available(conn)  # ~0.1ms
    else:
        # 2. If connection died, remove and create new one
        pool.remove_connection(conn)
        new_conn = await create_new_connection()
        pool.add_to_pool(new_conn)
```

### Connection States

```python
class ConnectionState:
    AVAILABLE = "available"    # Ready to be used
    IN_USE = "in_use"         # Currently executing queries
    IDLE = "idle"             # Available but been unused for a while
    TESTING = "testing"       # Being health-checked
    DEAD = "dead"             # Connection lost, needs replacement
```

---

## Pool Sizing and Configuration

### Pool Sizing Calculation

**Formula:**
```
pool_size = concurrent_db_operations × safety_factor
```

**Where:**
```
concurrent_db_operations = active_users × queries_per_request × (total_query_time / request_frequency)
```

### E-commerce Platform Example

**Scenario: Online Electronics Store**
```python
# Traffic analysis
peak_concurrent_users = 5000        # Black Friday traffic
queries_per_page_load = 4           # Product + reviews + related + inventory
average_query_time = 15             # 15ms per query (measured)
page_load_frequency = 30000         # User browses every 30 seconds

# Calculate concurrent operations
total_query_time_per_request = queries_per_page_load × average_query_time
# = 4 × 15ms = 60ms

concurrent_operations = peak_concurrent_users × (total_query_time_per_request / page_load_frequency)
# = 5000 × (60ms / 30000ms) = 10

# Apply safety factor
safety_factor = 1.5  # Buffer for traffic spikes
recommended_pool_size = concurrent_operations × safety_factor
# = 10 × 1.5 = 15 connections
```

### Different Request Types Analysis

```python
# Real e-commerce traffic breakdown
request_patterns = {
    "product_browse": {
        "percentage": 60,     # 60% of requests
        "queries": 4,         # Product + reviews + related + inventory
        "avg_duration": 12    # 12ms per query
    },
    "search": {
        "percentage": 25,     # 25% of requests  
        "queries": 6,         # Search + filters + facets + suggestions
        "avg_duration": 20    # 20ms per query (more complex)
    },
    "checkout": {
        "percentage": 10,     # 10% of requests
        "queries": 8,         # Cart + user + payment + inventory + orders
        "avg_duration": 25    # 25ms per query (transactions)
    },
    "user_account": {
        "percentage": 5,      # 5% of requests
        "queries": 3,         # User + orders + preferences  
        "avg_duration": 15    # 15ms per query
    }
}

# Calculate weighted concurrent operations
total_concurrent = 0
for pattern_name, config in request_patterns.items():
    percentage = config["percentage"] / 100
    queries = config["queries"] 
    duration = config["avg_duration"]
    
    pattern_load = peak_concurrent_users × percentage × (queries × duration / page_load_frequency)
    total_concurrent += pattern_load
    
    print(f"{pattern_name}: {pattern_load:.1f} concurrent operations")

# Results:
# product_browse: 5000 × 0.6 × (4×12ms / 30000ms) = 4.8
# search: 5000 × 0.25 × (6×20ms / 30000ms) = 5.0  
# checkout: 5000 × 0.1 × (8×25ms / 30000ms) = 3.3
# user_account: 5000 × 0.05 × (3×15ms / 30000ms) = 0.4
# Total: 13.5 concurrent operations

final_pool_size = 13.5 × 1.5 = 20 connections
```

### Infrastructure Constraints

```python
# Database server limits
postgresql_config = {
    "max_connections": 200,           # PostgreSQL setting
    "shared_buffers": "256MB",        # Memory per connection
    "effective_cache_size": "1GB"     # Total available memory
}

# Application deployment
deployment_config = {
    "app_servers": 3,                 # Number of FastAPI instances
    "app_server_pool_size": 20,       # Per server
    "total_app_connections": 60,      # 3 × 20
    "background_jobs": 10,            # ETL, analytics, backups
    "admin_connections": 5,           # DBA access, monitoring
    "total_used": 75                  # Out of 200 max
}

# Safety check
if deployment_config["total_used"] > postgresql_config["max_connections"] * 0.8:
    print("WARNING: Connection usage above 80% of database limit")
    print("Consider reducing pool sizes or upgrading database")
```

### Pool Configuration Examples

```python
# Conservative approach (financial services)
conservative_pool = {
    "min_size": 5,              # Always keep 5 connections warm
    "max_size": 15,             # Never exceed 15 connections
    "acquire_timeout": 30,      # Wait up to 30 seconds for connection
    "idle_timeout": 300,        # Close connections idle for 5 minutes
    "max_lifetime": 3600,       # Rotate connections every hour
    "health_check_interval": 60 # Check connection health every minute
}

# Aggressive approach (social media startup)  
aggressive_pool = {
    "min_size": 2,              # Keep minimal connections
    "max_size": 50,             # Scale up to 50 under load
    "acquire_timeout": 5,       # Fail fast if no connections
    "idle_timeout": 60,         # Close idle connections quickly
    "max_lifetime": 1800,       # Rotate connections every 30 minutes
    "health_check_interval": 30 # Check health every 30 seconds
}

# Balanced approach (e-commerce)
balanced_pool = {
    "min_size": 10,             # Reasonable baseline
    "max_size": 30,             # Handle traffic spikes
    "acquire_timeout": 10,      # Reasonable wait time
    "idle_timeout": 180,        # 3 minutes idle timeout
    "max_lifetime": 3600,       # Hourly rotation
    "health_check_interval": 60 # Minute health checks
}
```

---

## Implementation in FastAPI with PostgreSQL

### Basic Setup with asyncpg

```python
# database.py
import asyncpg
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class DatabasePool:
    def __init__(self):
        self.pool = None
        
    async def create_pool(self):
        """Create the connection pool during application startup."""
        try:
            self.pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="ecommerce_user", 
                password="secure_password",
                database="ecommerce_db",
                min_size=10,            # Minimum connections to maintain
                max_size=30,            # Maximum connections allowed
                max_queries=50000,      # Queries per connection before rotation
                max_inactive_connection_lifetime=300,  # 5 minutes
                timeout=60,             # Connection timeout
                connection_class=None,  # Custom connection class if needed
                init=self._init_connection  # Connection initialization
            )
            logger.info(f"Database pool created: {self.pool.get_size()} connections")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def _init_connection(self, conn):
        """Initialize each new connection."""
        # Set connection-specific settings
        await conn.execute("SET application_name = 'ecommerce_api'")
        await conn.execute("SET statement_timeout = '30s'")
        
    async def close_pool(self):
        """Close all connections in the pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection from the pool with automatic cleanup."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                # Log the error but let it propagate
                logger.error(f"Database operation failed: {e}")
                raise
    
    async def execute_query(self, query: str, *args):
        """Execute a query and return results."""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_one(self, query: str, *args):
        """Execute a query and return single result."""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_transaction(self, queries_and_params: list):
        """Execute multiple queries in a transaction."""
        async with self.get_connection() as conn:
            async with conn.transaction():
                results = []
                for query, params in queries_and_params:
                    result = await conn.fetch(query, *params)
                    results.append(result)
                return results
    
    def get_pool_stats(self):
        """Get current pool statistics."""
        if not self.pool:
            return {"status": "not_initialized"}
            
        return {
            "size": self.pool.get_size(),
            "min_size": self.pool.get_min_size(),
            "max_size": self.pool.get_max_size(),
            "idle_connections": self.pool.get_idle_size(),
            "status": "healthy"
        }

# Global pool instance
db_pool = DatabasePool()
```

### FastAPI Application with Pool Integration

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from database import db_pool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting up application...")
    await db_pool.create_pool()
    logger.info("Application ready")
    
    yield
    
    # Shutdown  
    logger.info("Shutting down application...")
    await db_pool.close_pool()
    logger.info("Application stopped")

app = FastAPI(lifespan=lifespan)

# Dependency to get database connection
async def get_db_connection():
    async with db_pool.get_connection() as conn:
        yield conn

@app.get("/health")
async def health_check():
    """Health check endpoint including database status."""
    try:
        pool_stats = db_pool.get_pool_stats()
        return {
            "status": "healthy",
            "database": pool_stats
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {e}")

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get product details with related data."""
    try:
        # Single connection handles multiple queries efficiently
        async with db_pool.get_connection() as conn:
            # Get product details
            product = await conn.fetchrow(
                """
                SELECT p.*, c.name as category_name 
                FROM products p 
                JOIN categories c ON p.category_id = c.id 
                WHERE p.id = $1
                """, 
                product_id
            )
            
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Get reviews (concurrent with inventory check)
            reviews_task = conn.fetch(
                """
                SELECT r.*, u.username 
                FROM reviews r 
                JOIN users u ON r.user_id = u.id 
                WHERE r.product_id = $1 
                ORDER BY r.created_at DESC 
                LIMIT 5
                """,
                product_id
            )
            
            inventory_task = conn.fetchrow(
                "SELECT quantity, reserved FROM inventory WHERE product_id = $1",
                product_id
            )
            
            # Wait for both queries
            reviews, inventory = await asyncio.gather(reviews_task, inventory_task)
            
            # Get related products
            related_products = await conn.fetch(
                """
                SELECT id, name, price, image_url 
                FROM products 
                WHERE category_id = $1 AND id != $2 
                LIMIT 4
                """,
                product['category_id'], product_id
            )
            
            return {
                "product": dict(product),
                "inventory": dict(inventory) if inventory else {"quantity": 0, "reserved": 0},
                "reviews": [dict(review) for review in reviews],
                "related_products": [dict(rp) for rp in related_products]
            }
            
    except asyncpg.PostgresError as e:
        logger.error(f"Database error for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error for product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/orders") 
async def create_order(order_data: dict):
    """Create a new order with transaction support."""
    try:
        # Use transaction for order creation
        queries_and_params = [
            (
                "INSERT INTO orders (user_id, total_amount, status) VALUES ($1, $2, $3) RETURNING id",
                (order_data['user_id'], order_data['total_amount'], 'pending')
            ),
            (
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
                (None, order_data['product_id'], order_data['quantity'], order_data['price'])  # order_id filled later
            ),
            (
                "UPDATE inventory SET quantity = quantity - $1, reserved = reserved + $1 WHERE product_id = $2",
                (order_data['quantity'], order_data['product_id'])
            )
        ]
        
        async with db_pool.get_connection() as conn:
            async with conn.transaction():
                # Create order
                order_result = await conn.fetchrow(
                    "INSERT INTO orders (user_id, total_amount, status) VALUES ($1, $2, $3) RETURNING id",
                    order_data['user_id'], order_data['total_amount'], 'pending'
                )
                order_id = order_result['id']
                
                # Create order items
                await conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES ($1, $2, $3, $4)",
                    order_id, order_data['product_id'], order_data['quantity'], order_data['price']
                )
                
                # Update inventory
                await conn.execute(
                    "UPDATE inventory SET quantity = quantity - $1, reserved = reserved + $1 WHERE product_id = $2",
                    order_data['quantity'], order_data['product_id']
                )
                
                return {"order_id": order_id, "status": "created"}
                
    except asyncpg.PostgresError as e:
        logger.error(f"Database error creating order: {e}")
        raise HTTPException(status_code=500, detail="Order creation failed")

@app.get("/admin/pool-stats")
async def get_pool_statistics():
    """Admin endpoint to monitor pool health."""
    return db_pool.get_pool_stats()
```

### Environment Configuration

```python
# config.py
import os
from pydantic import BaseSettings

class DatabaseSettings(BaseSettings):
    # Database connection
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "ecommerce_user"
    db_password: str = "secure_password"
    db_name: str = "ecommerce_db"
    
    # Pool configuration
    pool_min_size: int = 10
    pool_max_size: int = 30
    pool_max_queries: int = 50000
    pool_max_inactive_lifetime: int = 300
    pool_timeout: int = 60
    
    # Environment-specific overrides
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    class Config:
        env_file = ".env"

# Environment-specific configurations
class DevelopmentConfig(DatabaseSettings):
    pool_min_size: int = 2
    pool_max_size: int = 5
    
class ProductionConfig(DatabaseSettings):
    pool_min_size: int = 20
    pool_max_size: int = 50
    pool_timeout: int = 30
    
class TestingConfig(DatabaseSettings):
    db_name: str = "ecommerce_test_db"
    pool_min_size: int = 1
    pool_max_size: int = 2

# Factory function
def get_config():
    env = os.getenv("APP_ENV", "development")
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

settings = get_config()
```

---

## Pool Lifecycle Management

### Application Startup Process

```python
# startup.py
import asyncio
import logging
from database import db_pool
from config import settings

logger = logging.getLogger(__name__)

async def startup_sequence():
    """Complete application startup with proper error handling."""
    
    try:
        # 1. Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("Starting ecommerce application...")
        
        # 2. Create database pool
        logger.info("Initializing database connection pool...")
        await db_pool.create_pool()
        
        # 3. Warm up the pool (optional but recommended)
        logger.info("Warming up connection pool...")
        await warm_up_pool()
        
        # 4. Health check
        logger.info("Performing startup health checks...")
        await startup_health_check()
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        # Cleanup any partially initialized resources
        await cleanup_on_failure()
        raise

async def warm_up_pool():
    """Pre-create connections and test them."""
    try:
        # Execute a simple query to ensure connections work
        result = await db_pool.execute_one("SELECT 1 as health_check")
        if result['health_check'] != 1:
            raise Exception("Database health check failed")
            
        # Get pool stats to verify warm-up
        stats = db_pool.get_pool_stats()
        logger.info(f"Pool warmed up: {stats['size']}/{stats['max_size']} connections ready")
        
    except Exception as e:
        logger.error(f"Pool warm-up failed: {e}")
        raise

async def startup_health_check():
    """Verify all systems are operational."""
    checks = []
    
    # Database connectivity
    try:
        await db_pool.execute_one("SELECT version()")
        checks.append(("database", "healthy"))
    except Exception as e:
        checks.append(("database", f"unhealthy: {e}"))
        
    # Pool status
    stats = db_pool.get_pool_stats()
    if stats['size'] >= stats['min_size']:
        checks.append(("pool", "healthy"))
    else:
        checks.append(("pool", f"unhealthy: only {stats['size']} connections"))
    
    # Log results
    for component, status in checks:
        if "unhealthy" in status:
            logger.error(f"Health check failed - {component}: {status}")
            raise Exception(f"Startup health check failed: {component} is {status}")
        else:
            logger.info(f"Health check passed - {component}: {status}")

async def cleanup_on_failure():
    """Clean up resources if startup fails."""
    try:
        if db_pool.pool:
            await db_pool.close_pool()
            logger.info("Cleaned up database pool after startup failure")
    except Exception as e:
        logger.error(f"Error during startup cleanup: {e}")
```

### Graceful Shutdown Process

```python
# shutdown.py
import asyncio
import signal
import logging
from database import db_pool

logger = logging.getLogger(__name__)

class GracefulShutdown:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.active_requests = 0
        self.max_shutdown_wait = 30  # seconds
        
    async def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        loop = asyncio.get_running_loop()
        
        # Handle SIGTERM (container shutdown)
        loop.add_signal_handler(signal.SIGTERM, self.handle_shutdown_signal)
        
        # Handle SIGINT (Ctrl+C)  
        loop.add_signal_handler(signal.SIGINT, self.handle_shutdown_signal)
        
    def handle_shutdown_signal(self):
        """Handle shutdown signals."""
        logger.info("Received shutdown signal, starting graceful shutdown...")
        self.shutdown_event.set()
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal and handle gracefully."""
        await self.shutdown_event.wait()
        await self.graceful_shutdown()
    
    async def graceful_shutdown(self):
        """Perform graceful shutdown sequence."""
        logger.info("Starting graceful shutdown sequence...")
        
        try:
            # 1. Stop accepting new requests (handled by web server)
            logger.info("Stopping new request acceptance...")
            
            # 2. Wait for active requests to complete
            await self.wait_for_active_requests()
            
            # 3. Close database connections
            logger.info("Closing database connection pool...")
            await db_pool.close_pool()
            
            # 4. Final cleanup
            logger.info("Performing final cleanup...")
            await self.final_cleanup()
            
            logger.info("Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")
            # Force shutdown if graceful fails
            await self.force_shutdown()
    
    async def wait_for_active_requests(self):
        """Wait for active database requests to complete."""
        start_time = asyncio.get_event_loop().time()
        
        while self.active_requests > 0:
            elapsed = asyncio.get_event_loop().time() - start_time
            
            if elapsed > self.max_shutdown_wait:
                logger.warning(f"Shutdown timeout reached, {self.active_requests} requests still active")
                break
                
            logger.info(f"Waiting for {self.active_requests} active requests to complete...")
            await asyncio.sleep(1)
        
        if self.active_requests == 0:
            logger.info("All active requests completed")
    
    async def final_cleanup(self):
        """Perform final cleanup tasks."""
        # Cancel any remaining background tasks
        tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if tasks:
            logger.info(f"Cancelling {len(tasks)} remaining tasks...")
            for task in tasks:
                task.cancel()
            
            # Wait for tasks to be cancelled
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def force_shutdown(self):
        """Force shutdown if graceful shutdown fails."""
        logger.warning("Forcing immediate shutdown...")
        try:
            await db_pool.close_pool()
        except:
            pass

# Global shutdown handler
shutdown_handler = GracefulShutdown()

# Request tracking middleware
class RequestTrackingMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            shutdown_handler.active_requests += 1
            try:
                await self.app(scope, receive, send)
            finally:
                shutdown_handler.active_requests -= 1
        else:
            await self.app(scope, receive, send)
```

### Pool Monitoring and Health Checks

```python
# monitoring.py
import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from database import db_pool

logger = logging.getLogger(__name__)

class PoolMonitor:
    def __init__(self):
        self.metrics = {
            "connection_acquisitions": 0,
            "connection_timeouts": 0,
            "failed_connections": 0,
            "total_queries": 0,
            "query_times": [],
            "pool_size_history": [],
            "last_health_check": None
        }
        self.alert_thresholds = {
            "max_acquisition_time": 5.0,      # seconds
            "max_pool_utilization": 0.8,      # 80%
            "min_available_connections": 2,    # minimum free connections
            "max_failed_connections_rate": 0.1 # 10% failure rate
        }
        
    async def start_monitoring(self):
        """Start background monitoring tasks."""
        asyncio.create_task(self.periodic_health_check())
        asyncio.create_task(self.collect_metrics())
        logger.info("Pool monitoring started")
    
    async def periodic_health_check(self):
        """Perform periodic health checks."""
        while True:
            try:
                await self.health_check()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                await asyncio.sleep(30)  # Retry more frequently on failure
    
    async def collect_metrics(self):
        """Collect and store pool metrics."""
        while True:
            try:
                stats = db_pool.get_pool_stats()
                self.metrics["pool_size_history"].append({
                    "timestamp": datetime.now(),
                    "size": stats["size"],
                    "idle": stats["idle_connections"],
                    "utilization": (stats["size"] - stats["idle_connections"]) / stats["max_size"]
                })
                
                # Keep only last 24 hours of data
                cutoff = datetime.now() - timedelta(hours=24)
                self.metrics["pool_size_history"] = [
                    entry for entry in self.metrics["pool_size_history"] 
                    if entry["timestamp"] > cutoff
                ]
                
                # Check for alerts
                await self.check_alerts(stats)
                
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                await asyncio.sleep(60)
    
    async def health_check(self):
        """Comprehensive health check."""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            result = await db_pool.execute_one("SELECT 1 as health_check")
            if result["health_check"] != 1:
                raise Exception("Basic health check query failed")
            
            # Test connection acquisition time
            acquisition_start = time.time()
            async with db_pool.get_connection() as conn:
                acquisition_time = time.time() - acquisition_start
                
                # Test query execution
                await conn.fetchrow("SELECT current_timestamp")
            
            # Record metrics
            total_time = time.time() - start_time
            self.metrics["last_health_check"] = {
                "timestamp": datetime.now(),
                "status": "healthy",
                "acquisition_time": acquisition_time,
                "total_time": total_time
            }
            
            logger.debug(f"Health check passed in {total_time:.3f}s")
            
        except Exception as e:
            self.metrics["last_health_check"] = {
                "timestamp": datetime.now(),
                "status": "unhealthy",
                "error": str(e)
            }
            logger.error(f"Health check failed: {e}")
            raise
    
    async def check_alerts(self, stats):
        """Check if any alert conditions are met."""
        alerts = []
        
        # High pool utilization
        utilization = (stats["size"] - stats["idle_connections"]) / stats["max_size"]
        if utilization > self.alert_thresholds["max_pool_utilization"]:
            alerts.append(f"High pool utilization: {utilization:.1%}")
        
        # Low available connections
        if stats["idle_connections"] < self.alert_thresholds["min_available_connections"]:
            alerts.append(f"Low available connections: {stats['idle_connections']}")
        
        # Slow connection acquisition
        if self.metrics["last_health_check"] and "acquisition_time" in self.metrics["last_health_check"]:
            acq_time = self.metrics["last_health_check"]["acquisition_time"]
            if acq_time > self.alert_thresholds["max_acquisition_time"]:
                alerts.append(f"Slow connection acquisition: {acq_time:.2f}s")
        
        # Send alerts if any conditions are met
        if alerts:
            await self.send_alerts(alerts)
    
    async def send_alerts(self, alerts: List[str]):
        """Send alerts to monitoring system."""
        for alert in alerts:
            logger.warning(f"POOL ALERT: {alert}")
            # In production, send to Slack, PagerDuty, etc.
            # await slack_webhook.send(f"🚨 Database Pool Alert: {alert}")
    
    def get_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report."""
        if not self.metrics["pool_size_history"]:
            return {"status": "no_data"}
        
        recent_history = self.metrics["pool_size_history"][-60:]  # Last 30 minutes
        
        avg_utilization = sum(entry["utilization"] for entry in recent_history) / len(recent_history)
        max_utilization = max(entry["utilization"] for entry in recent_history)
        
        return {
            "current_status": self.metrics["last_health_check"],
            "pool_stats": db_pool.get_pool_stats(),
            "utilization": {
                "average_30min": avg_utilization,
                "peak_30min": max_utilization,
                "current": recent_history[-1]["utilization"] if recent_history else 0
            },
            "metrics": {
                "total_acquisitions": self.metrics["connection_acquisitions"],
                "timeout_rate": self.metrics["connection_timeouts"] / max(self.metrics["connection_acquisitions"], 1),
                "failure_rate": self.metrics["failed_connections"] / max(self.metrics["connection_acquisitions"], 1),
                "total_queries": self.metrics["total_queries"]
            },
            "recommendations": self.get_recommendations()
        }
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        stats = db_pool.get_pool_stats()
        
        # Pool size recommendations
        if not self.metrics["pool_size_history"]:
            return recommendations
            
        recent_utilization = [entry["utilization"] for entry in self.metrics["pool_size_history"][-20:]]
        avg_utilization = sum(recent_utilization) / len(recent_utilization)
        
        if avg_utilization > 0.8:
            recommendations.append("Consider increasing pool size - high utilization detected")
        elif avg_utilization < 0.3:
            recommendations.append("Consider decreasing pool size - low utilization detected")
        
        # Timeout recommendations
        timeout_rate = self.metrics["connection_timeouts"] / max(self.metrics["connection_acquisitions"], 1)
        if timeout_rate > 0.05:  # 5%
            recommendations.append("High timeout rate - consider increasing pool size or timeout values")
        
        return recommendations

# Global monitor instance
pool_monitor = PoolMonitor()

# Middleware to track connection usage
class ConnectionMetricsMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            pool_monitor.metrics["connection_acquisitions"] += 1
            
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                if "timeout" in str(e).lower():
                    pool_monitor.metrics["connection_timeouts"] += 1
                else:
                    pool_monitor.metrics["failed_connections"] += 1
                raise
            finally:
                query_time = time.time() - start_time
                pool_monitor.metrics["query_times"].append(query_time)
                pool_monitor.metrics["total_queries"] += 1
                
                # Keep only recent query times
                if len(pool_monitor.metrics["query_times"]) > 1000:
                    pool_monitor.metrics["query_times"] = pool_monitor.metrics["query_times"][-500:]
        else:
            await self.app(scope, receive, send)
```

---

## Monitoring and Maintenance

### Daily Operations Checklist

**Morning Health Check (5 minutes):**
```python
# morning_check.py
async def morning_health_check():
    """Daily morning health check routine."""
    print("🌅 Morning Database Pool Health Check")
    print("=" * 50)
    
    # 1. Pool Status
    stats = db_pool.get_pool_stats()
    print(f"Pool Size: {stats['size']}/{stats['max_size']}")
    print(f"Idle Connections: {stats['idle_connections']}")
    print(f"Utilization: {((stats['size'] - stats['idle_connections']) / stats['max_size']) * 100:.1f}%")
    
    # 2. Recent Performance
    report = pool_monitor.get_monitoring_report()
    print(f"Average Utilization (30min): {report['utilization']['average_30min'] * 100:.1f}%")
    print(f"Peak Utilization (30min): {report['utilization']['peak_30min'] * 100:.1f}%")
    
    # 3. Error Rates
    metrics = report['metrics']
    print(f"Timeout Rate: {metrics['timeout_rate'] * 100:.2f}%")
    print(f"Failure Rate: {metrics['failure_rate'] * 100:.2f}%")
    
    # 4. Recommendations
    recommendations = report['recommendations']
    if recommendations:
        print("\n⚠️  Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print("\n✅ No recommendations - pool operating optimally")
    
    # 5. Database Server Health
    async with db_pool.get_connection() as conn:
        # Check active connections on database server
        active_conns = await conn.fetchrow("""
            SELECT count(*) as total_connections,
                   count(*) FILTER (WHERE state = 'active') as active_connections,
                   count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        
        print(f"\nDatabase Server Status:")
        print(f"Total Connections: {active_conns['total_connections']}")
        print(f"Active Queries: {active_conns['active_connections']}")
        print(f"Idle Connections: {active_conns['idle_connections']}")
```

### Weekly Performance Analysis

```python
# weekly_analysis.py
async def weekly_performance_analysis():
    """Weekly deep dive into pool performance."""
    print("📊 Weekly Pool Performance Analysis")
    print("=" * 50)
    
    # Get 7 days of metrics
    week_history = [
        entry for entry in pool_monitor.metrics["pool_size_history"]
        if entry["timestamp"] > datetime.now() - timedelta(days=7)
    ]
    
    if not week_history:
        print("❌ Insufficient data for weekly analysis")
        return
    
    # Calculate statistics
    utilizations = [entry["utilization"] for entry in week_history]
    sizes = [entry["size"] for entry in week_history]
    
    print(f"Pool Utilization Statistics (7 days):")
    print(f"  Average: {sum(utilizations) / len(utilizations) * 100:.1f}%")
    print(f"  Maximum: {max(utilizations) * 100:.1f}%")
    print(f"  Minimum: {min(utilizations) * 100:.1f}%")
    print(f"  95th Percentile: {sorted(utilizations)[int(len(utilizations) * 0.95)] * 100:.1f}%")
    
    print(f"\nPool Size Statistics:")
    print(f"  Average: {sum(sizes) / len(sizes):.1f}")
    print(f"  Maximum: {max(sizes)}")
    print(f"  Minimum: {min(sizes)}")
    
    # Identify peak hours
    hourly_utilization = {}
    for entry in week_history:
        hour = entry["timestamp"].hour
        if hour not in hourly_utilization:
            hourly_utilization[hour] = []
        hourly_utilization[hour].append(entry["utilization"])
    
    peak_hours = sorted(
        hourly_utilization.items(),
        key=lambda x: sum(x[1]) / len(x[1]),
        reverse=True
    )[:3]
    
    print(f"\nPeak Usage Hours:")
    for hour, utils in peak_hours:
        avg_util = sum(utils) / len(utils)
        print(f"  {hour:02d}:00 - {avg_util * 100:.1f}% average utilization")
    
    # Capacity planning recommendations
    max_observed_utilization = max(utilizations)
    current_max_size = db_pool.get_pool_stats()["max_size"]
    
    if max_observed_utilization > 0.85:
        recommended_size = int(current_max_size * (max_observed_utilization / 0.75))
        print(f"\n📈 Capacity Planning:")
        print(f"  Current max pool size: {current_max_size}")
        print(f"  Peak utilization: {max_observed_utilization * 100:.1f}%")
        print(f"  Recommended max size: {recommended_size}")
        print(f"  Safety buffer: {(recommended_size - current_max_size)} connections")
```

### Performance Monitoring Dashboard

```python
# dashboard.py - Add to FastAPI app
@app.get("/admin/pool-dashboard")
async def pool_dashboard():
    """Admin dashboard for pool monitoring."""
    report = pool_monitor.get_monitoring_report()
    
    # Get additional database metrics
    async with db_pool.get_connection() as conn:
        # Slow queries
        slow_queries = await conn.fetch("""
            SELECT query, calls, total_time, mean_time, rows
            FROM pg_stat_statements 
            WHERE mean_time > 100  -- Queries taking >100ms on average
            ORDER BY mean_time DESC 
            LIMIT 10
        """)
        
        # Connection details
        connections = await conn.fetch("""
            SELECT application_name, state, count(*) as connection_count
            FROM pg_stat_activity 
            WHERE datname = current_database()
            GROUP BY application_name, state
            ORDER BY connection_count DESC
        """)
        
        # Database size and activity
        db_stats = await conn.fetchrow("""
            SELECT 
                pg_database_size(current_database()) as db_size_bytes,
                (SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()) as total_connections,
                (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
        """)
    
    return {
        "pool_status": report,
        "database_metrics": {
            "size_mb": db_stats["db_size_bytes"] // (1024 * 1024),
            "connections": {
                "current": db_stats["total_connections"],
                "max": db_stats["max_connections"],
                "utilization": db_stats["total_connections"] / db_stats["max_connections"]
            }
        },
        "slow_queries": [dict(row) for row in slow_queries],
        "connection_breakdown": [dict(row) for row in connections],
        "recommendations": report["recommendations"]
    }

@app.get("/admin/pool-metrics")
async def pool_metrics():
    """Endpoint for monitoring tools (Prometheus, etc.)."""
    stats = db_pool.get_pool_stats()
    metrics = pool_monitor.metrics
    
    return {
        "pool_size": stats["size"],
        "pool_max_size": stats["max_size"],
        "pool_idle_connections": stats["idle_connections"],
        "pool_utilization": (stats["size"] - stats["idle_connections"]) / stats["max_size"],
        "total_acquisitions": metrics["connection_acquisitions"],
        "timeout_count": metrics["connection_timeouts"],
        "failure_count": metrics["failed_connections"],
        "total_queries": metrics["total_queries"],
        "avg_query_time": sum(metrics["query_times"][-100:]) / len(metrics["query_times"][-100:]) if metrics["query_times"] else 0
    }
```

---

## Troubleshooting Common Issues

### Issue 1: Connection Pool Exhaustion

**Symptoms:**
- Users getting "connection timeout" errors
- Application becomes unresponsive
- Error logs showing "pool acquire timeout"

**Diagnosis:**
```python
async def diagnose_pool_exhaustion():
    """Diagnose connection pool exhaustion."""
    print("🔍 Diagnosing Pool Exhaustion")
    print("=" * 30)
    
    stats = db_pool.get_pool_stats()
    print(f"Pool Status: {stats['idle_connections']}/{stats['size']} available")
    
    # Check for long-running queries
    async with db_pool.get_connection() as conn:
        long_queries = await conn.fetch("""
            SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
            FROM pg_stat_activity 
            WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
            AND state = 'active'
            ORDER BY duration DESC
        """)
        
        if long_queries:
            print(f"⚠️  Found {len(long_queries)} long-running queries:")
            for query in long_queries[:5]:
                print(f"  PID {query['pid']}: {query['duration']} - {query['query'][:100]}...")
        
        # Check for idle connections in transaction
        idle_in_txn = await conn.fetch("""
            SELECT pid, now() - state_change AS duration, state
            FROM pg_stat_activity 
            WHERE state = 'idle in transaction'
            AND (now() - state_change) > interval '1 minute'
        """)
        
        if idle_in_txn:
            print(f"⚠️  Found {len(idle_in_txn)} idle transactions:")
            for txn in idle_in_txn:
                print(f"  PID {txn['pid']}: idle for {txn['duration']}")
```

**Solutions:**
```python
# Solution 1: Increase pool size temporarily
async def emergency_pool_resize():
    """Emergency pool resize for immediate relief."""
    current_stats = db_pool.get_pool_stats()
    new_size = min(current_stats["max_size"] * 2, 100)  # Double size, max 100
    
    print(f"Emergency resize: {current_stats['max_size']} → {new_size}")
    # Note: This would require pool recreation in most implementations
    
# Solution 2: Kill problematic connections
async def kill_problematic_queries():
    """Kill long-running or problematic queries."""
    async with db_pool.get_connection() as conn:
        # Kill queries running longer than 10 minutes
        killed = await conn.fetch("""
            SELECT pg_terminate_backend(pid) as killed, pid, query
            FROM pg_stat_activity 
            WHERE (now() - pg_stat_activity.query_start) > interval '10 minutes'
            AND state = 'active'
            AND query NOT LIKE '%pg_stat_activity%'
        """)
        
        print(f"Killed {len(killed)} long-running queries")
        return killed

# Solution 3: Implement connection timeouts
class TimeoutConnectionPool(DatabasePool):
    async def get_connection_with_timeout(self, timeout: float = 5.0):
        """Get connection with custom timeout."""
        try:
            return await asyncio.wait_for(
                self.get_connection(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise Exception(f"Failed to acquire connection within {timeout}s")
```

### Issue 2: Memory Leaks in Connections

**Symptoms:**
- Gradual increase in database server memory usage
- Connections consuming more RAM over time
- Database performance degrading

**Diagnosis:**
```python
async def diagnose_memory_leaks():
    """Check for connection memory issues."""
    async with db_pool.get_connection() as conn:
        # Check connection memory usage
        memory_stats = await conn.fetch("""
            SELECT 
                application_name,
                state,
                backend_start,
                now() - backend_start as connection_age,
                query_start,
                now() - query_start as query_age
            FROM pg_stat_activity 
            WHERE datname = current_database()
            ORDER BY backend_start
        """)
        
        # Look for very old connections
        old_connections = [
            conn for conn in memory_stats 
            if conn["connection_age"] and conn["connection_age"].total_seconds() > 3600  # 1 hour
        ]
        
        if old_connections:
            print(f"Found {len(old_connections)} connections older than 1 hour")
            for conn in old_connections[:5]:
                print(f"  Age: {conn['connection_age']}, State: {conn['state']}")
```

**Solutions:**
```python
# Solution 1: Implement connection rotation
class RotatingConnectionPool(DatabasePool):
    def __init__(self, max_connection_lifetime=3600):  # 1 hour
        super().__init__()
        self.max_connection_lifetime = max_connection_lifetime
        self.connection_birth_times = {}
    
    async def _should_rotate_connection(self, conn_id):
        """Check if connection should be rotated."""
        if conn_id not in self.connection_birth_times:
            return False
            
        age = time.time() - self.connection_birth_times[conn_id]
        return age > self.max_connection_lifetime
    
    async def rotate_old_connections(self):
        """Rotate connections that are too old."""
        # Implementation would replace old connections with new ones
        pass

# Solution 2: Monitor prepared statement cache
async def monitor_prepared_statements():
    """Monitor prepared statement usage."""
    async with db_pool.get_connection() as conn:
        stmt_stats = await conn.fetch("""
            SELECT name, statement, calls, total_time, mean_time
            FROM pg_prepared_statements 
            ORDER BY calls DESC
        """)
        
        if len(stmt_stats) > 1000:  # Too many prepared statements
            print(f"Warning: {len(stmt_stats)} prepared statements may cause memory issues")
```

### Issue 3: Slow Query Performance

**Symptoms:**
- Increasing response times
- High database CPU usage
- Queries taking longer than expected

**Diagnosis:**
```python
async def diagnose_slow_queries():
    """Identify and analyze slow queries."""
    async with db_pool.get_connection() as conn:
        # Enable pg_stat_statements if not already enabled
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
        
        # Get slowest queries
        slow_queries = await conn.fetch("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                (total_time/sum(total_time) OVER()) * 100 as pct_total_time
            FROM pg_stat_statements 
            WHERE calls > 10  -- Only queries called more than 10 times
            ORDER BY mean_time DESC 
            LIMIT 20
        """)
        
        print("🐌 Slowest Queries (by average time):")
        for i, query in enumerate(slow_queries[:10], 1):
            print(f"{i}. {query['mean_time']:.2f}ms avg, {query['calls']} calls")
            print(f"   {query['query'][:100]}...")
            print(f"   {query['pct_total_time']:.1f}% of total DB time\n")
        
        # Check for missing indexes
        missing_indexes = await conn.fetch("""
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE n_distinct > 100 
            AND correlation < 0.1
            ORDER BY n_distinct DESC
            LIMIT 10
        """)
        
        if missing_indexes:
            print("🔍 Potential Missing Indexes:")
            for idx in missing_indexes:
                print(f"  {idx['tablename']}.{idx['attname']} (distinct: {idx['n_distinct']})")
```

**Solutions:**
```python
# Solution 1: Query optimization
async def optimize_queries():
    """Provide query optimization suggestions."""
    suggestions = [
        "Add LIMIT clauses to prevent full table scans",
        "Use EXPLAIN ANALYZE to identify bottlenecks",
        "Consider adding indexes on frequently filtered columns",
        "Use connection pooling for frequently accessed data",
        "Implement query result caching for expensive operations"
    ]
    
    return suggestions

# Solution 2: Implement query timeout
class QueryTimeoutPool(DatabasePool):
    async def execute_with_timeout(self, query: str, *args, timeout: float = 30.0):
        """Execute query with timeout."""
        async with self.get_connection() as conn:
            try:
                return await asyncio.wait_for(
                    conn.fetch(query, *args),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                # Cancel the query on the database side
                await conn.cancel()
                raise Exception(f"Query timed out after {timeout}s")

# Solution 3: Connection-level optimizations
async def optimize_connection_settings():
    """Optimize PostgreSQL connection settings."""
    optimizations = {
        "work_mem": "64MB",                    # Memory for sorts/joins
        "effective_cache_size": "2GB",        # OS cache size hint
        "random_page_cost": "1.1",            # SSD optimization
        "effective_io_concurrency": "200",    # SSD concurrent I/O
        "wal_buffers": "16MB",                # WAL buffer size
        "checkpoint_completion_target": "0.9", # Checkpoint timing
        "shared_preload_libraries": "'pg_stat_statements'" # Query statistics
    }
    
    async with db_pool.get_connection() as conn:
        for setting, value in optimizations.items():
            try:
                await conn.execute(f"SET {setting} = {value}")
                print(f"✅ Set {setting} = {value}")
            except Exception as e:
                print(f"❌ Failed to set {setting}: {e}")
```

### Issue 4: Connection Leaks

**Symptoms:**
- Pool size grows over time
- Database reporting more connections than expected
- Memory usage gradually increasing

**Diagnosis:**
```python
async def diagnose_connection_leaks():
    """Detect connection leaks."""
    # Monitor pool size over time
    initial_stats = db_pool.get_pool_stats()
    
    # Wait and check again
    await asyncio.sleep(300)  # 5 minutes
    
    final_stats = db_pool.get_pool_stats()
    
    if final_stats["size"] > initial_stats["size"]:
        print(f"⚠️ Potential leak: Pool grew from {initial_stats['size']} to {final_stats['size']}")
        
        # Check database for connections
        async with db_pool.get_connection() as conn:
            app_connections = await conn.fetch("""
                SELECT application_name, count(*) as conn_count
                FROM pg_stat_activity 
                WHERE datname = current_database()
                GROUP BY application_name
                ORDER BY conn_count DESC
            """)
            
            print("Database connections by application:")
            for app_conn in app_connections:
                print(f"  {app_conn['application_name']}: {app_conn['conn_count']}")

# Solution: Connection tracking
class LeakDetectionPool(DatabasePool):
    def __init__(self):
        super().__init__()
        self.connection_tracker = {}
        
    async def track_connection_usage(self, conn_id, operation):
        """Track connection acquisition and release."""
        if operation == "acquire":
            self.connection_tracker[conn_id] = {
                "acquired_at": time.time(),
                "stack_trace": "".join(traceback.format_stack())
            }
        elif operation == "release":
            if conn_id in self.connection_tracker:
                usage_time = time.time() - self.connection_tracker[conn_id]["acquired_at"]
                if usage_time > 300:  # 5 minutes
                    print(f"⚠️ Long-held connection: {usage_time:.1f}s")
                    print(f"Stack trace: {self.connection_tracker[conn_id]['stack_trace']}")
                del self.connection_tracker[conn_id]
```

---

## Advanced Topics

### Connection Pool Failover and High Availability

**Multi-Database Setup:**
```python
# ha_pool.py - High Availability Connection Pool
import asyncio
import random
from typing import List, Optional
from enum import Enum

class DatabaseRole(Enum):
    PRIMARY = "primary"
    REPLICA = "replica"
    OFFLINE = "offline"

class HighAvailabilityPool:
    def __init__(self, primary_config: dict, replica_configs: List[dict]):
        self.primary_config = primary_config
        self.replica_configs = replica_configs
        self.primary_pool = None
        self.replica_pools = []
        self.primary_status = DatabaseRole.PRIMARY
        self.replica_status = {}
        self.failover_threshold = 3  # failures before failover
        self.current_failures = 0
        
    async def initialize(self):
        """Initialize all database pools."""
        # Create primary pool
        try:
            self.primary_pool = await asyncpg.create_pool(**self.primary_config)
            await self._health_check_database(self.primary_pool)
            self.primary_status = DatabaseRole.PRIMARY
        except Exception as e:
            logger.error(f"Primary database initialization failed: {e}")
            self.primary_status = DatabaseRole.OFFLINE
        
        # Create replica pools
        for i, replica_config in enumerate(self.replica_configs):
            try:
                replica_pool = await asyncpg.create_pool(**replica_config)
                await self._health_check_database(replica_pool)
                self.replica_pools.append(replica_pool)
                self.replica_status[i] = DatabaseRole.REPLICA
            except Exception as e:
                logger.error(f"Replica {i} initialization failed: {e}")
                self.replica_pools.append(None)
                self.replica_status[i] = DatabaseRole.OFFLINE
    
    async def _health_check_database(self, pool):
        """Check if database is healthy."""
        async with pool.acquire() as conn:
            result = await conn.fetchrow("SELECT 1 as health_check")
            if result["health_check"] != 1:
                raise Exception("Health check failed")
    
    async def get_write_connection(self):
        """Get connection for write operations (primary only)."""
        if self.primary_status == DatabaseRole.PRIMARY:
            try:
                async with self.primary_pool.acquire() as conn:
                    yield conn
                self.current_failures = 0  # Reset failure count on success
            except Exception as e:
                self.current_failures += 1
                logger.error(f"Primary database error: {e}")
                
                if self.current_failures >= self.failover_threshold:
                    await self._initiate_failover()
                raise
        else:
            raise Exception("Primary database is offline - writes not available")
    
    async def get_read_connection(self):
        """Get connection for read operations (primary or replica)."""
        # Try primary first if available
        if self.primary_status == DatabaseRole.PRIMARY:
            try:
                async with self.primary_pool.acquire() as conn:
                    yield conn
                return
            except Exception as e:
                logger.warning(f"Primary read failed, trying replicas: {e}")
        
        # Try replicas
        available_replicas = [
            (i, pool) for i, pool in enumerate(self.replica_pools)
            if pool and self.replica_status.get(i) == DatabaseRole.REPLICA
        ]
        
        if not available_replicas:
            raise Exception("No readable databases available")
        
        # Randomly select a replica for load balancing
        replica_idx, replica_pool = random.choice(available_replicas)
        
        try:
            async with replica_pool.acquire() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Replica {replica_idx} failed: {e}")
            self.replica_status[replica_idx] = DatabaseRole.OFFLINE
            # Recursively try other replicas
            await self.get_read_connection()
    
    async def _initiate_failover(self):
        """Initiate failover to replica."""
        logger.critical("Initiating database failover!")
        self.primary_status = DatabaseRole.OFFLINE
        
        # Promote first available replica to primary
        for i, replica_pool in enumerate(self.replica_pools):
            if replica_pool and self.replica_status.get(i) == DatabaseRole.REPLICA:
                try:
                    # In real implementation, would promote replica to primary
                    # This is database-specific (e.g., PostgreSQL streaming replication)
                    await self._promote_replica_to_primary(i)
                    
                    self.primary_pool = replica_pool
                    self.primary_status = DatabaseRole.PRIMARY
                    self.replica_pools[i] = None
                    self.replica_status[i] = DatabaseRole.OFFLINE
                    
                    logger.info(f"Failover complete: Replica {i} promoted to primary")
                    break
                except Exception as e:
                    logger.error(f"Failed to promote replica {i}: {e}")
                    continue
    
    async def _promote_replica_to_primary(self, replica_idx):
        """Promote replica to primary (implementation depends on DB setup)."""
        # This would involve database-specific commands
        # For PostgreSQL with streaming replication:
        # 1. Stop replica
        # 2. Promote using pg_promote() or pg_ctl promote
        # 3. Update application configuration
        pass

# Usage in FastAPI
ha_pool = HighAvailabilityPool(
    primary_config={
        "host": "primary-db.company.com",
        "port": 5432,
        "user": "app_user",
        "password": "password",
        "database": "ecommerce",
        "min_size": 10,
        "max_size": 30
    },
    replica_configs=[
        {
            "host": "replica1-db.company.com",
            "port": 5432,
            "user": "app_user", 
            "password": "password",
            "database": "ecommerce",
            "min_size": 5,
            "max_size": 20
        },
        {
            "host": "replica2-db.company.com",
            "port": 5432,
            "user": "app_user",
            "password": "password", 
            "database": "ecommerce",
            "min_size": 5,
            "max_size": 20
        }
    ]
)

@app.get("/products/{product_id}")
async def get_product_ha(product_id: int):
    """Get product using HA pool."""
    async with ha_pool.get_read_connection() as conn:
        product = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", product_id
        )
        return dict(product) if product else None

@app.post("/orders")
async def create_order_ha(order_data: dict):
    """Create order using HA pool."""
    async with ha_pool.get_write_connection() as conn:
        async with conn.transaction():
            order = await conn.fetchrow(
                "INSERT INTO orders (user_id, total) VALUES ($1, $2) RETURNING id",
                order_data["user_id"], order_data["total"]
            )
            return {"order_id": order["id"]}
```

### Kubernetes Integration and Scaling

```python
# k8s_pool.py - Kubernetes-aware connection pool
import os
import asyncio
from kubernetes import client, config, watch

class KubernetesAwarePool(DatabasePool):
    def __init__(self):
        super().__init__()
        self.namespace = os.getenv("KUBERNETES_NAMESPACE", "default")
        self.service_name = os.getenv("DB_SERVICE_NAME", "postgresql")
        self.k8s_client = None
        self.endpoints_cache = {}
        
    async def initialize_k8s(self):
        """Initialize Kubernetes client."""
        try:
            # Load in-cluster config if running in pod
            config.load_incluster_config()
        except:
            # Load local config for development
            config.load_kube_config()
        
        self.k8s_client = client.CoreV1Api()
        
        # Start watching for endpoint changes
        asyncio.create_task(self._watch_endpoints())
    
    async def _watch_endpoints(self):
        """Watch for database endpoint changes."""
        w = watch.Watch()
        
        while True:
            try:
                for event in w.stream(
                    self.k8s_client.list_namespaced_endpoints,
                    namespace=self.namespace,
                    field_selector=f"metadata.name={self.service_name}"
                ):
                    await self._handle_endpoint_change(event)
            except Exception as e:
                logger.error(f"Kubernetes endpoint watch failed: {e}")
                await asyncio.sleep(30)  # Retry after 30 seconds
    
    async def _handle_endpoint_change(self, event):
        """Handle database endpoint changes."""
        event_type = event["type"]
        endpoint = event["object"]
        
        if event_type in ["ADDED", "MODIFIED"]:
            # Extract new database endpoints
            new_endpoints = []
            for subset in endpoint.subsets or []:
                for address in subset.addresses or []:
                    for port in subset.ports or []:
                        if port.name == "postgresql":
                            new_endpoints.append({
                                "host": address.ip,
                                "port": port.port
                            })
            
            # Update connection pool if endpoints changed
            if new_endpoints != self.endpoints_cache.get("postgresql", []):
                logger.info(f"Database endpoints changed: {new_endpoints}")
                self.endpoints_cache["postgresql"] = new_endpoints
                await self._recreate_pool_with_new_endpoints(new_endpoints)
    
    async def _recreate_pool_with_new_endpoints(self, endpoints):
        """Recreate pool with new database endpoints."""
        if not endpoints:
            logger.error("No database endpoints available")
            return
        
        # For simplicity, use first endpoint
        # In production, implement load balancing across all endpoints
        primary_endpoint = endpoints[0]
        
        # Close existing pool
        if self.pool:
            await self.pool.close()
        
        # Create new pool with updated endpoint
        self.pool = await asyncpg.create_pool(
            host=primary_endpoint["host"],
            port=primary_endpoint["port"],
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            min_size=int(os.getenv("POOL_MIN_SIZE", "10")),
            max_size=int(os.getenv("POOL_MAX_SIZE", "30"))
        )
        
        logger.info(f"Pool recreated with endpoint {primary_endpoint}")

# Deployment configuration
# k8s-deployment.yaml
"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    metadata:
      labels:
        app: ecommerce-api
    spec:
      containers:
      - name: api
        image: ecommerce-api:latest
        env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: password
        - name: DB_SERVICE_NAME
          value: "postgresql"
        - name: POOL_MIN_SIZE
          value: "5"  # Smaller per-pod pool since we have multiple pods
        - name: POOL_MAX_SIZE
          value: "15"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""
```

### Advanced Monitoring and Alerting

```python
# advanced_monitoring.py
import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List

class AdvancedPoolMonitor:
    def __init__(self):
        self.metrics_store = []
        self.alert_handlers = []
        self.alert_cooldowns = {}  # Prevent alert spam
        
    async def setup_monitoring(self):
        """Setup comprehensive monitoring."""
        # Start background tasks
        asyncio.create_task(self._collect_detailed_metrics())
        asyncio.create_task(self._analyze_trends())
        asyncio.create_task(self._capacity_planning())
        
        # Setup alert handlers
        self.alert_handlers = [
            SlackAlertHandler(),
            PagerDutyAlertHandler(),
            EmailAlertHandler()
        ]
    
    async def _collect_detailed_metrics(self):
        """Collect detailed pool and database metrics."""
        while True:
            try:
                timestamp = datetime.now()
                
                # Pool metrics
                pool_stats = db_pool.get_pool_stats()
                
                # Database metrics
                async with db_pool.get_connection() as conn:
                    db_metrics = await self._collect_db_metrics(conn)
                
                # System metrics
                system_metrics = await self._collect_system_metrics()
                
                # Store comprehensive metrics
                metric_entry = {
                    "timestamp": timestamp,
                    "pool": pool_stats,
                    "database": db_metrics,
                    "system": system_metrics
                }
                
                self.metrics_store.append(metric_entry)
                
                # Keep only last 24 hours
                cutoff = timestamp - timedelta(hours=24)
                self.metrics_store = [
                    m for m in self.metrics_store 
                    if m["timestamp"] > cutoff
                ]
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Metrics collection failed: {e}")
                await asyncio.sleep(60)
    
    async def _collect_db_metrics(self, conn):
        """Collect detailed database metrics."""
        # Connection statistics
        conn_stats = await conn.fetchrow("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_txn
            FROM pg_stat_activity 
            WHERE datname = current_database()
        """)
        
        # Database performance
        db_stats = await conn.fetchrow("""
            SELECT 
                numbackends,
                xact_commit,
                xact_rollback,
                blks_read,
                blks_hit,
                tup_returned,
                tup_fetched,
                tup_inserted,
                tup_updated,
                tup_deleted
            FROM pg_stat_database 
            WHERE datname = current_database()
        """)
        
        # Lock information
        locks = await conn.fetchrow("""
            SELECT 
                count(*) as total_locks,
                count(*) FILTER (WHERE granted = false) as waiting_locks
            FROM pg_locks 
            WHERE database = (SELECT oid FROM pg_database WHERE datname = current_database())
        """)
        
        return {
            "connections": dict(conn_stats),
            "performance": dict(db_stats),
            "locks": dict(locks)
        }
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # In production, use proper monitoring tools
        # This is a simplified example
        return {
            "cpu_usage": 0,  # Would get from system monitoring
            "memory_usage": 0,
            "disk_io": 0,
            "network_io": 0
        }
    
    async def _analyze_trends(self):
        """Analyze metrics for trends and anomalies."""
        while True:
            try:
                if len(self.metrics_store) < 10:
                    await asyncio.sleep(300)  # Need more data
                    continue
                
                # Analyze pool utilization trends
                recent_metrics = self.metrics_store[-20:]  # Last 10 minutes
                utilizations = [
                    (m["pool"]["size"] - m["pool"]["idle_connections"]) / m["pool"]["max_size"]
                    for m in recent_metrics
                ]
                
                avg_utilization = sum(utilizations) / len(utilizations)
                trend = self._calculate_trend(utilizations)
                
                # Check for concerning trends
                alerts = []
                
                if avg_utilization > 0.85:
                    alerts.append(PoolAlert(
                        level="warning",
                        message=f"High pool utilization: {avg_utilization:.1%}",
                        metric="pool_utilization",
                        value=avg_utilization
                    ))
                
                if trend > 0.1:  # Growing by 10% per measurement
                    alerts.append(PoolAlert(
                        level="warning", 
                        message=f"Pool utilization trending up: {trend:.1%} per minute",
                        metric="pool_utilization_trend",
                        value=trend
                    ))
                
                # Send alerts if any
                for alert in alerts:
                    await self._send_alert(alert)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Trend analysis failed: {e}")
                await asyncio.sleep(300)
    
    def _calculate_trend(self, values):
        """Calculate linear trend in values."""
        if len(values) < 2:
            return 0
        
        # Simple linear regression slope
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * values[i] for i in range(n))
        x2_sum = sum(i * i for i in range(n))
        
        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
        return slope
    
    async def _send_alert(self, alert):
        """Send alert through configured channels."""
        # Check cooldown to prevent spam
        cooldown_key = f"{alert.metric}_{alert.level}"
        last_sent = self.alert_cooldowns.get(cooldown_key)
        
        if last_sent and datetime.now() - last_sent < timedelta(minutes=15):
            return  # Still in cooldown
        
        # Send alert through all handlers
        for handler in self.alert_handlers:
            try:
                await handler.send_alert(alert)
            except Exception as e:
                logger.error(f"Alert handler {handler.__class__.__name__} failed: {e}")
        
        # Update cooldown
        self.alert_cooldowns[cooldown_key] = datetime.now()

class PoolAlert:
    def __init__(self, level: str, message: str, metric: str, value: float):
        self.level = level
        self.message = message
        self.metric = metric
        self.value = value
        self.timestamp = datetime.now()

class SlackAlertHandler:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    async def send_alert(self, alert: PoolAlert):
        """Send alert to Slack."""
        if not self.webhook_url:
            return
        
        color = {
            "info": "#36a64f",
            "warning": "#ff9900", 
            "critical": "#ff0000"
        }.get(alert.level, "#cccccc")
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"🔄 Database Pool Alert - {alert.level.upper()}",
                "text": alert.message,
                "fields": [
                    {"title": "Metric", "value": alert.metric, "short": True},
                    {"title": "Value", "value": f"{alert.value:.3f}", "short": True},
                    {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                ],
                "footer": "Database Pool Monitor"
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)

class PagerDutyAlertHandler:
    def __init__(self):
        self.integration_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
    
    async def send_alert(self, alert: PoolAlert):
        """Send alert to PagerDuty."""
        if not self.integration_key or alert.level != "critical":
            return  # Only send critical alerts to PagerDuty
        
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": f"pool-{alert.metric}",
            "payload": {
                "summary": alert.message,
                "source": "database-pool-monitor",
                "severity": "error",
                "custom_details": {
                    "metric": alert.metric,
                    "value": alert.value,
                    "timestamp": alert.timestamp.isoformat()
                }
            }
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.api_url, json=payload)

class EmailAlertHandler:
    async def send_alert(self, alert: PoolAlert):
        """Send email alert (implementation depends on email service)."""
        # Implementation would use SMTP or email service API
        logger.info(f"Email alert: {alert.message}")
```

---

## Real-World Case Studies

### Case Study 1: E-commerce Flash Sale

**Scenario:** Black Friday flash sale with 50x normal traffic

**Problem:**
```python
# Normal traffic: 1,000 concurrent users
# Flash sale: 50,000 concurrent users
# Pool size: 20 connections
# Result: Massive timeouts and site crash

normal_load = {
    "concurrent_users": 1000,
    "pool_size": 20,
    "avg_response_time": "150ms",
    "error_rate": "0.1%"
}

flash_sale_load = {
    "concurrent_users": 50000,
    "pool_size": 20,  # Same as normal
    "avg_response_time": "15000ms",  # 15 seconds!
    "error_rate": "35%"  # Site essentially down
}
```

**Solution Implementation:**
```python
# flash_sale_pool.py
class FlashSalePool:
    def __init__(self):
        self.normal_pool_size = 20
        self.flash_sale_pool_size = 100
        self.current_mode = "normal"
        self.traffic_threshold = 5000  # Switch at 5k concurrent users
        
    async def auto_scale_for_traffic(self, current_users: int):
        """Automatically scale pool based on traffic."""
        if current_users > self.traffic_threshold and self.current_mode == "normal":
            await self._scale_up_for_flash_sale()
        elif current_users < self.traffic_threshold and self.current_mode == "flash_sale":
            await self._scale_down_to_normal()
    
    async def _scale_up_for_flash_sale(self):
        """Scale up for high traffic."""
        logger.info("Scaling up for flash sale traffic")
        
        # Pre-create additional connections
        for _ in range(self.flash_sale_pool_size - self.normal_pool_size):
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                await self.pool.putconn(conn)
            except Exception as e:
                logger.error(f"Failed to create additional connection: {e}")
        
        self.current_mode = "flash_sale"
        
        # Also implement read replicas for read-heavy operations
        await self._enable_read_replicas()
    
    async def _enable_read_replicas(self):
        """Enable read replicas to distribute load."""
        # Route product browsing to read replicas
        # Keep writes (orders, cart updates) on primary
        pass

# Traffic monitoring for auto-scaling
class TrafficMonitor:
    def __init__(self):
        self.current_users = 0
        self.request_rate = 0
        
    async def monitor_traffic(self):
        """Monitor traffic and trigger scaling."""
        while True:
            # Get current metrics (from application metrics)
            current_metrics = await self._get_current_metrics()
            
            self.current_users = current_metrics["concurrent_users"]
            self.request_rate = current_metrics["requests_per_second"]
            
            # Trigger auto-scaling
            await flash_sale_pool.auto_scale_for_traffic(self.current_users)
            
            await asyncio.sleep(60)  # Check every minute
```

**Results:**
```python
# After optimization:
optimized_flash_sale = {
    "concurrent_users": 50000,
    "pool_size": 100,  # Scaled up
    "read_replicas": 3,  # Added read replicas
    "avg_response_time": "400ms",  # Much better
    "error_rate": "2%",  # Acceptable
    "revenue_impact": "+300%"  # Sale successful
}
```

### Case Study 2: Financial Services Compliance

**Scenario:** Banking application requiring audit trails and connection security

**Requirements:**
- All database connections must be audited
- Connection pools must support connection-level encryption
- Idle connections must be terminated after 15 minutes
- Failed connection attempts must be logged and monitored

**Implementation:**
```python
# secure_banking_pool.py
import ssl
import logging
from datetime import datetime, timedelta

class SecureBankingPool(DatabasePool):
    def __init__(self):
        super().__init__()
        self.connection_audit_log = []
        self.failed_attempts = []
        self.max_idle_time = 900  # 15 minutes
        self.ssl_context = self._create_ssl_context()
        
    def _create_ssl_context(self):
        """Create SSL context for secure connections."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Load client certificates
        context.load_cert_chain(
            certfile="/etc/ssl/certs/client.crt",
            keyfile="/etc/ssl/private/client.key"
        )
        
        # Load CA certificate
        context.load_verify_locations("/etc/ssl/certs/ca.crt")
        
        return context
    
    async def create_secure_pool(self):
        """Create pool with security configurations."""
        self.pool = await asyncpg.create_pool(
            host="secure-db.bank.com",
            port=5432,
            user="banking_app",
            password=os.getenv("DB_PASSWORD"),
            database="banking_db",
            ssl=self.ssl_context,
            min_size=5,
            max_size=25,
            max_queries=10000,  # Rotate connections frequently
            max_inactive_connection_lifetime=self.max_idle_time,
            init=self._init_secure_connection,
            setup=self._setup_connection_audit
        )
    
    async def _init_secure_connection(self, conn):
        """Initialize each connection with security settings."""
        # Set connection-specific security parameters
        await conn.execute("SET application_name = 'banking_app'")
        await conn.execute("SET log_connections = on")
        await conn.execute("SET log_disconnections = on")
        await conn.execute("SET log_statement = 'all'")  # Log all statements
        
        # Record connection creation
        self._audit_connection_event(conn, "CONNECTED")
    
    async def _setup_connection_audit(self, conn):
        """Setup audit logging for connection."""
        # Add connection-specific audit ID
        audit_id = f"conn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(conn)}"
        await conn.execute(f"SET session.audit_id = '{audit_id}'")
    
    def _audit_connection_event(self, conn, event_type: str, details: str = ""):
        """Audit connection events."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "connection_id": id(conn),
            "event_type": event_type,
            "user": "banking_app",
            "details": details,
            "source_ip": "10.0.1.100"  # Application server IP
        }
        
        self.connection_audit_log.append(audit_entry)
        
        # Also log to secure audit system
        secure_logger = logging.getLogger("audit")
        secure_logger.info(f"DB_AUDIT: {json.dumps(audit_entry)}")
    
    async def get_audited_connection(self, user_id: str, operation: str):
        """Get connection with full audit trail."""
        try:
            async with self.pool.acquire() as conn:
                # Record operation start
                self._audit_connection_event(
                    conn, 
                    "OPERATION_START", 
                    f"user={user_id}, operation={operation}"
                )
                
                yield conn
                
                # Record operation success
                self._audit_connection_event(
                    conn, 
                    "OPERATION_SUCCESS", 
                    f"user={user_id}, operation={operation}"
                )
                
        except Exception as e:
            # Record operation failure
            self._audit_connection_event(
                conn if 'conn' in locals() else None,
                "OPERATION_FAILURE",
                f"user={user_id}, operation={operation}, error={str(e)}"
            )
            
            # Log security-relevant failures
            if "authentication" in str(e).lower():
                self.failed_attempts.append({
                    "timestamp": datetime.now(),
                    "user": user_id,
                    "error": str(e),
                    "source_ip": "10.0.1.100"
                })
            
            raise
    
    async def generate_compliance_report(self, start_date: datetime, end_date: datetime):
        """Generate compliance report for auditors."""
        relevant_logs = [
            log for log in self.connection_audit_log
            if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
        ]
        
        report = {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_connections": len([l for l in relevant_logs if l["event_type"] == "CONNECTED"]),
                "total_operations": len([l for l in relevant_logs if "OPERATION" in l["event_type"]]),
                "failed_operations": len([l for l in relevant_logs if l["event_type"] == "OPERATION_FAILURE"]),
                "security_incidents": len(self.failed_attempts)
            },
            "detailed_logs": relevant_logs,
            "security_events": self.failed_attempts
        }
        
        return report

# Usage in banking application
@app.post("/transfer")
async def bank_transfer(transfer_data: dict, current_user: str):
    """Secure bank transfer with full audit trail."""
    async with secure_pool.get_audited_connection(current_user, "TRANSFER") as conn:
        async with conn.transaction():
            # Debit source account
            await conn.execute(
                "UPDATE accounts SET balance = balance - $1 WHERE account_id = $2",
                transfer_data["amount"], transfer_data["from_account"]
            )
            
            # Credit destination account
            await conn.execute(
                "UPDATE accounts SET balance = balance + $1 WHERE account_id = $2", 
                transfer_data["amount"], transfer_data["to_account"]
            )
            
            # Record transaction
            await conn.execute(
                "INSERT INTO transactions (from_account, to_account, amount, user_id) VALUES ($1, $2, $3, $4)",
                transfer_data["from_account"], transfer_data["to_account"], 
                transfer_data["amount"], current_user
            )
            
            return {"status": "success", "transaction_id": "TXN_12345"}
```

---

## Best Practices Checklist

### Development Phase

**✅ Pool Configuration:**
- [ ] Pool size calculated based on expected concurrent operations
- [ ] Minimum pool size set to handle baseline traffic
- [ ] Maximum pool size respects database connection limits
- [ ] Connection timeouts configured appropriately
- [ ] Connection lifetime limits set to prevent stale connections

**✅ Code Implementation:**
- [ ] Always use `async with` for connection management
- [ ] Implement proper error handling for pool exhaustion
- [ ] Use transactions for multi-statement operations
- [ ] Avoid long-running operations while holding connections
- [ ] Implement connection health checks

**✅ Environment Configuration:**
- [ ] Different pool sizes for dev/staging/production
- [ ] Database credentials stored securely (not in code)
- [ ] Connection parameters tuned for each environment
- [ ] SSL/TLS enabled for production databases
- [ ] Firewall rules restricting database access

### Production Deployment

**✅ Monitoring Setup:**
- [ ] Pool utilization metrics collected
- [ ] Connection acquisition time monitored
- [ ] Database performance metrics tracked
- [ ] Alert thresholds configured for pool exhaustion
- [ ] Health check endpoints implemented

**✅ Operational Procedures:**
- [ ] Daily health check routine established
- [ ] Weekly performance analysis scheduled
- [ ] Emergency scaling procedures documented
- [ ] Failover procedures tested and documented
- [ ] Backup and recovery procedures validated

**✅ Performance Optimization:**
- [ ] Query performance analyzed and optimized
- [ ] Database indexes reviewed and optimized
- [ ] Connection pool settings tuned based on real traffic
- [ ] Read replicas implemented for read-heavy workloads
- [ ] Caching strategies implemented to reduce database load

### Security and Compliance

**✅ Security Measures:**
- [ ] Database connections encrypted with SSL/TLS
- [ ] Connection credentials rotated regularly
- [ ] Audit logging enabled for all database operations
- [ ] Access controls implemented and reviewed
- [ ] Vulnerability scanning performed regularly

**✅ Compliance Requirements:**
- [ ] Audit trails maintained for regulatory compliance
- [ ] Data retention policies implemented
- [ ] Privacy controls in place for sensitive data
- [ ] Compliance reports generated regularly
- [ ] Security incident response procedures documented

### Maintenance and Operations

**✅ Regular Maintenance:**
```python
# monthly_maintenance.py
async def monthly_pool_maintenance():
    """Monthly maintenance checklist."""
    tasks = [
        "Review pool utilization trends",
        "Analyze slow query reports", 
        "Check connection leak indicators",
        "Validate backup and recovery procedures",
        "Review and rotate database credentials",
        "Update monitoring thresholds based on traffic changes",
        "Performance test pool under load",
        "Review and update documentation"
    ]
    
    for task in tasks:
        print(f"□ {task}")
```

**✅ Incident Response:**
```python
# incident_response.py
class PoolIncidentResponse:
    def __init__(self):
        self.severity_levels = {
            "P1": "Pool completely unavailable",
            "P2": "Pool performance severely degraded", 
            "P3": "Pool performance moderately degraded",
            "P4": "Pool showing warning signs"
        }
        
        self.response_procedures = {
            "P1": [
                "Scale up pool size immediately",
                "Kill long-running queries",
                "Restart application if necessary",
                "Enable read replicas if available",
                "Notify on-call engineer"
            ],
            "P2": [
                "Increase pool size",
                "Analyze slow queries",
                "Check for connection leaks",
                "Monitor closely for 30 minutes"
            ],
            "P3": [
                "Monitor pool metrics",
                "Schedule performance analysis",
                "Review recent application changes"
            ],
            "P4": [
                "Document warning signs",
                "Schedule maintenance window",
                "Review capacity planning"
            ]
        }
    
    async def handle_incident(self, severity: str, description: str):
        """Handle pool-related incident."""
        print(f"🚨 INCIDENT: {severity} - {description}")
        print(f"Severity: {self.severity_levels[severity]}")
        print("Response procedures:")
        
        for i, procedure in enumerate(self.response_procedures[severity], 1):
            print(f"  {i}. {procedure}")
```

### Performance Tuning Guidelines

**Connection Pool Optimization:**
```python
# performance_tuning.py
class PoolPerformanceTuner:
    def __init__(self):
        self.tuning_guidelines = {
            "high_throughput": {
                "description": "High request volume, short-lived connections",
                "pool_size": "Large (50-100)",
                "min_size": "25% of max_size",
                "connection_lifetime": "Short (30 minutes)",
                "acquire_timeout": "Low (5 seconds)"
            },
            "low_latency": {
                "description": "Low latency requirements, predictable load",
                "pool_size": "Medium (20-50)",
                "min_size": "50% of max_size", 
                "connection_lifetime": "Medium (1 hour)",
                "acquire_timeout": "Very low (2 seconds)"
            },
            "batch_processing": {
                "description": "Background jobs, long-running queries",
                "pool_size": "Small (5-15)",
                "min_size": "10% of max_size",
                "connection_lifetime": "Long (2 hours)",
                "acquire_timeout": "High (30 seconds)"
            },
            "mixed_workload": {
                "description": "Combination of web and batch processing", 
                "pool_size": "Medium (30-60)",
                "min_size": "30% of max_size",
                "connection_lifetime": "Medium (1 hour)",
                "acquire_timeout": "Medium (10 seconds)"
            }
        }
    
    def recommend_settings(self, workload_type: str, traffic_pattern: dict):
        """Recommend pool settings based on workload."""
        if workload_type not in self.tuning_guidelines:
            return "Unknown workload type"
        
        base_recommendation = self.tuning_guidelines[workload_type]
        
        # Adjust based on traffic pattern
        peak_ratio = traffic_pattern.get("peak_to_average_ratio", 2.0)
        if peak_ratio > 5.0:
            base_recommendation["pool_size"] += " (increase for high variance)"
        
        return base_recommendation

# Usage example
tuner = PoolPerformanceTuner()
recommendation = tuner.recommend_settings("high_throughput", {
    "peak_to_average_ratio": 3.0,
    "average_requests_per_second": 1000,
    "peak_requests_per_second": 3000
})
```

### Troubleshooting Quick Reference

**Common Issues and Solutions:**

```python
# troubleshooting_guide.py
class TroubleshootingGuide:
    def __init__(self):
        self.common_issues = {
            "connection_timeouts": {
                "symptoms": ["Users getting timeout errors", "High response times", "Pool exhaustion alerts"],
                "causes": ["Pool size too small", "Long-running queries", "Connection leaks", "Database overload"],
                "solutions": [
                    "Increase pool size temporarily",
                    "Identify and kill long-running queries", 
                    "Check for connection leaks in application code",
                    "Add query timeouts",
                    "Scale database if needed"
                ],
                "prevention": [
                    "Monitor pool utilization trends",
                    "Set appropriate connection timeouts",
                    "Use connection tracking middleware",
                    "Regular performance testing"
                ]
            },
            
            "slow_performance": {
                "symptoms": ["Increasing response times", "High database CPU", "Query backlog"],
                "causes": ["Unoptimized queries", "Missing indexes", "Lock contention", "Database maintenance needed"],
                "solutions": [
                    "Analyze slow query logs",
                    "Add missing indexes",
                    "Optimize expensive queries",
                    "Implement query caching",
                    "Consider read replicas"
                ],
                "prevention": [
                    "Regular query performance review",
                    "Automated index analysis",
                    "Query execution plan monitoring",
                    "Capacity planning"
                ]
            },
            
            "memory_leaks": {
                "symptoms": ["Gradual memory increase", "Connection pool growing", "Database memory alerts"],
                "causes": ["Connection not properly released", "Prepared statement accumulation", "Transaction not closed"],
                "solutions": [
                    "Implement connection lifecycle tracking",
                    "Add connection rotation",
                    "Clear prepared statement cache",
                    "Audit transaction handling"
                ],
                "prevention": [
                    "Always use context managers",
                    "Set connection lifetime limits",
                    "Monitor prepared statement counts",
                    "Code review for resource management"
                ]
            },
            
            "failover_issues": {
                "symptoms": ["Connection failures after database restart", "Inconsistent error rates", "Split-brain scenarios"],
                "causes": ["Poor health checking", "Inadequate failover logic", "DNS caching issues"],
                "solutions": [
                    "Implement robust health checks",
                    "Improve failover detection logic",
                    "Clear DNS cache",
                    "Manual failover if needed"
                ],
                "prevention": [
                    "Regular failover testing",
                    "Health check automation",
                    "Multiple failover triggers",
                    "Documentation of procedures"
                ]
            }
        }
    
    def diagnose(self, symptoms: list):
        """Diagnose issues based on symptoms."""
        matches = []
        
        for issue, details in self.common_issues.items():
            symptom_overlap = set(symptoms) & set(details["symptoms"])
            if symptom_overlap:
                matches.append({
                    "issue": issue,
                    "confidence": len(symptom_overlap) / len(details["symptoms"]),
                    "details": details
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
    
    def get_solution_steps(self, issue: str):
        """Get step-by-step solution for an issue."""
        if issue not in self.common_issues:
            return "Issue not found in guide"
        
        return self.common_issues[issue]["solutions"]

# Usage example
guide = TroubleshootingGuide()
symptoms = ["Users getting timeout errors", "High response times"]
diagnosis = guide.diagnose(symptoms)

print("Diagnosis results:")
for match in diagnosis:
    print(f"- {match['issue']} (confidence: {match['confidence']:.1%})")
    if match['confidence'] > 0.5:
        print("  Solutions:")
        for solution in match['details']['solutions']:
            print(f"    • {solution}")
```

### Advanced Configuration Examples

**Production-Ready Configuration:**
```python
# production_config.py
class ProductionPoolConfig:
    def __init__(self):
        self.configs = {
            "ecommerce_primary": {
                "host": os.getenv("DB_PRIMARY_HOST"),
                "port": 5432,
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": "ecommerce_prod",
                "min_size": 20,
                "max_size": 80,
                "max_queries": 50000,
                "max_inactive_connection_lifetime": 1800,  # 30 minutes
                "timeout": 30,
                "connection_class": None,
                "ssl": "require",
                "init": self._init_production_connection
            },
            
            "analytics_replica": {
                "host": os.getenv("DB_REPLICA_HOST"),
                "port": 5432,
                "user": os.getenv("DB_READ_USER"),
                "password": os.getenv("DB_READ_PASSWORD"),
                "database": "ecommerce_prod",
                "min_size": 5,
                "max_size": 30,
                "max_queries": 10000,
                "max_inactive_connection_lifetime": 600,  # 10 minutes
                "timeout": 15,
                "ssl": "require",
                "init": self._init_readonly_connection
            }
        }
    
    async def _init_production_connection(self, conn):
        """Initialize production connection with optimizations."""
        await conn.execute("SET application_name = 'ecommerce_api_prod'")
        await conn.execute("SET statement_timeout = '30s'")
        await conn.execute("SET lock_timeout = '10s'")
        await conn.execute("SET idle_in_transaction_session_timeout = '5min'")
        await conn.execute("SET log_min_duration_statement = 1000")  # Log slow queries
    
    async def _init_readonly_connection(self, conn):
        """Initialize read-only connection for analytics."""
        await conn.execute("SET application_name = 'ecommerce_analytics'")
        await conn.execute("SET default_transaction_read_only = on")
        await conn.execute("SET statement_timeout = '300s'")  # Longer timeout for analytics
        await conn.execute("SET work_mem = '256MB'")  # More memory for complex queries

# Environment-specific overrides
class EnvironmentConfig:
    @staticmethod
    def get_config():
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            return ProductionPoolConfig().configs
        elif env == "staging":
            return StagingPoolConfig().configs
        elif env == "development":
            return DevelopmentPoolConfig().configs
        else:
            raise ValueError(f"Unknown environment: {env}")
```

### Final Recommendations

**For Junior Developers Becoming Senior:**

1. **Start Simple, Scale Smart:**
   - Begin with basic pool configuration
   - Monitor and adjust based on real traffic
   - Don't over-engineer initially

2. **Master the Fundamentals:**
   - Understand connection lifecycle
   - Know when and why to use different pool sizes
   - Learn to read pool metrics and database statistics

3. **Build Operational Excellence:**
   - Implement comprehensive monitoring
   - Create runbooks for common issues
   - Practice incident response procedures

4. **Think Beyond Code:**
   - Consider business impact of pool decisions
   - Understand cost implications of scaling
   - Plan for capacity growth

5. **Continuous Learning:**
   - Stay updated with database best practices
   - Learn from production incidents
   - Share knowledge with team members

**Remember:** Connection pooling is not just about performance—it's about building reliable, scalable systems that can handle real-world challenges while maintaining business continuity.

---

## Conclusion

Database connection pooling is a critical skill for senior developers. This guide provides the foundation for understanding, implementing, and maintaining production-grade connection pools. The key to mastery is combining theoretical knowledge with hands-on experience, continuous monitoring, and iterative improvement based on real-world usage patterns.

As you progress in your career, remember that the best pool configuration is one that balances performance, reliability, and operational simplicity while meeting your specific business requirements.

**Next Steps:**
1. Implement a basic pool in your current project
2. Set up monitoring and alerting
3. Test under realistic load conditions
4. Document your configuration decisions
5. Share learnings with your team

Good luck on your journey from junior to senior developer! 🚀