"""# Problem: Async Database Connection Pool with Circuit Breaker

**Scenario:** You're building a high-performance async application that needs to handle database operations safely, even when the database becomes unreliable.

**Requirements:** Create a `DatabasePool` class that:

1. **Connection Pool Management**:
   * Maintains a pool of async database connections (simulate with `asyncio.sleep()`)
   * Pool size configurable (default 5 connections)
   * Connections can be acquired/released safely by multiple coroutines

2. **Circuit Breaker Pattern**:
   * **CLOSED state**: Normal operation, allows all requests
   * **OPEN state**: Database is failing, immediately reject requests for 30 seconds
   * **HALF-OPEN state**: After 30 seconds, allow 1 test request to check if DB recovered
   * Switch to OPEN after 3 consecutive failures
   * Switch back to CLOSED after 1 successful request in HALF-OPEN

3. **Database Operations**:
   * Simulate `query(sql)` method with:
    * 20% chance of `DatabaseError("Connection failed")`
    * 80% chance of success returning `{"Result for: {sql}"`}`
    * Each operation takes 0.5-1.5 seconds

4. **Async Context Manager**:
   * Support `async with pool.get_connection()` as conn: pattern
   * Automatically acquire/release connections
   * Handle connection failures gracefully

5. **Monitoring**:
   * Track: total_requests, successful_requests, failed_requests, circuit_state
   * Provide `get_stats()` method

**Class structure:**

```python
class DatabasePool:
    def __init__(self, pool_size=5, failure_threshold=3, recovery_timeout=30):
    # Your implementation

    async def get_connection(self):
    # Return async context manager

    async def query(self, sql: str):
    # Execute query through the pool

    def get_stats(self):
    # Return statistics dictionary
```

**Test scenario:**

```python
async def main():
    pool = DatabasePool(pool_size=3, failure_threshold=2)

    # Simulate 20 concurrent database operations
    tasks = [pool.query("SELECT * FROM table_(1)") for i in range(20)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print(pool.get_stats())
```

This is the most complex problem - it combines:
    * Resource management (connection pooling)
    * State machines (circuit breaker)
    * Concurrency control
    * Error handling
    * Context managers
"""

# pylint: disable=pointless-string-statement, line-too-long
"""# Complete scenarios with lock mechanisms for all circuit breaker states:

## Scenario 1: CLOSED State → Multiple Failures → OPEN
```plaintext
Initial State: Circuit CLOSED, failure_count = 1, semaphore allows 5 concurrent

Time 0ms: 10 requests arrive simultaneously
├─ 5 requests get semaphore slots immediately  
└─ 5 requests wait in semaphore queue

Time 0.001ms: Circuit breaker check (no lock needed - just reading CLOSED state)
├─ All 5 allowed requests proceed to database
└─ 5 waiting requests still in semaphore queue

Time 0.002ms: 5 database operations start simultaneously
Time 100ms: All 5 database operations complete with FAILURE

Time 100.001ms: All 5 failed requests try to update failure counter simultaneously (they started concurrently, but each takes different time to complete their own operation, so the completion time is more likely different, making the sequential-like behavior below possible. Note: Acquiring and releasing the lock happens at microseconds, very fast)
├─ Request D acquires lock: failure_count = 1 → 2, releases lock
├─ Request E acquires lock: failure_count = 2 → 3 → Circuit OPENS, releases lock  
├─ Request B acquires lock: sees circuit is OPEN, releases lock
├─ Request A acquires lock: sees circuit is OPEN, releases lock
└─ Request C acquires lock: sees circuit is OPEN, releases lock

Time 100.002ms: Circuit is now OPEN, semaphore releases 5 slots
Time 100.003ms: 5 waiting requests acquire semaphore slots
Time 100.004ms: 5 waiting requests check circuit breaker → all get CircuitBreakerError
```

### Scenario 2: HALF_OPEN State → Test Succeeds
```plaintext
Initial State: Circuit HALF_OPEN, failure_count = 3, test_in_progress = False

Time 0ms: 8 requests arrive simultaneously

Time 0.001ms: All 8 requests try circuit breaker check simultaneously
├─ Request C acquires lock first: test_in_progress = False → True, allowed = True
├─ Request A acquires lock: test_in_progress = True, allowed = False  
├─ Request B acquires lock: test_in_progress = True, allowed = False
├─ ... (Requests D,E,F,G,H all get allowed = False)
└─ 7 requests immediately get CircuitBreakerError

Time 0.002ms: Only Request C proceeds to semaphore
Time 0.003ms: Request C acquires semaphore slot
Time 0.004ms: Request C starts database operation (alone)
Time 200ms: Request C completes with SUCCESS

Time 200.001ms: Request C calls record_success()
├─ Request C acquires lock: failure_count = 3 → 0, circuit = CLOSED, test_in_progress = False
└─ Request C releases lock

Time 200.002ms: Circuit is now CLOSED, ready for normal operations
```

### Scenario 3: HALF_OPEN State → Test Fails
```plaintext
Initial State: Circuit HALF_OPEN, failure_count = 3, test_in_progress = False

Time 0ms: 6 requests arrive simultaneously

Time 0.001ms: Race condition at circuit breaker check
├─ Request F wins lock: test_in_progress = False → True, allowed = True
└─ Requests A,B,C,D,E lose: get CircuitBreakerError immediately

Time 0.002ms: Only Request F proceeds to database
Time 300ms: Request F completes with FAILURE

Time 300.001ms: Request F calls record_failure()
├─ Request F acquires lock: failure_count = 3 → 4, circuit = OPEN, test_in_progress = False
└─ Request F releases lock

Time 300.002ms: Circuit is back to OPEN for another 30 seconds
```

### Scenario 4: Mixed Success/Failure in CLOSED State
```plaintext
Initial State: Circuit CLOSED, failure_count = 1

Time 0ms: 5 requests start database operations simultaneously
Time 150ms: Mixed results - 3 SUCCESS, 2 FAILURE

Time 150.001ms: All 5 requests try to update counters simultaneously
├─ Request A (success) acquires lock: failure_count = 1 → 0, releases lock
├─ Request B (failure) acquires lock: failure_count = 0 → 1, releases lock
├─ Request C (success) acquires lock: failure_count = 1 → 0, releases lock  
├─ Request D (failure) acquires lock: failure_count = 0 → 1, releases lock
└─ Request E (success) acquires lock: failure_count = 1 → 0, releases lock

Time 150.002ms: Final state - Circuit CLOSED, failure_count = 0
```

## Key Lock Behaviors:
- Reading circuit state: No lock needed (just checking a variable)
- HALF_OPEN competition: Lock ensures exactly 1 winner
- Counter updates: Lock prevents race conditions on shared failure_count
- State transitions: Happen atomically within the locked section

The locks are surgical - they only protect the tiny critical sections, not the expensive database operations!"""

import asyncio
import random
import logging


class ColoredFormatter(logging.Formatter):
    # ANSI color codes
    # ALL_CAPS naming convention indicates these are constants
    ANSI_COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(
        self, fmt=None, datefmt=None, style="%", validate=True, *, defaults=None
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.ANSI_COLORS:
            record.levelname = f"{self.ANSI_COLORS[record.levelname]}{record.levelname}{self.ANSI_COLORS["RESET"]}"
        return super().format(record)


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class CircuitBreakerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DatabasePool:
    def __init__(
        self, pool_size: int = 5, failure_threshold: int = 3, recovery_timeout: int = 30
    ):
        self.pool_size = pool_size
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.semaphore = asyncio.Semaphore(pool_size)
        self.circuit_state = "CLOSED"
        self.failure_count = 0
        self._lock = asyncio.Lock()
        self.test_in_progress = False
        self.allowed_request = False
        self.circuit_open_time = None

    def get_connection(self):
        # Return async context manager
        return self.semaphore  # Semaphore is the context manager

    async def execute_query(self, sql: str):
        async with self.get_connection():
            # Simulate DB operation
            await asyncio.sleep(random.uniform(0.5, 1.5))

            try:
                rand_num = random.random()
                if rand_num < 0.2:  # 20% chance of failure
                    logger.debug(
                        'Query "%s" got DatabaseError, rand_num=%.4f',
                        sql,
                        rand_num,
                    )
                    raise DatabaseError("Connection Failed")

                logger.info(
                    'Database operation successful for query "%s", circuit_state=%s',
                    sql,
                    self.circuit_state,
                )
                return f"Result for {sql}"

            except DatabaseError as e:
                logger.error(
                    'Database operation failed for query "%s": %s', sql, str(e)
                )
                # Re-raise with additional context
                raise DatabaseError(
                    f"Query failed: {sql}. Original error: {str(e)}"
                ) from e

    async def query(self, sql: str):
        # First, check circuit state and get permission to proceed
        is_test_request = False

        async with self._lock:
            logger.debug(
                'Processing query "%s", current state: %s', sql, self.circuit_state
            )

            # Check if we need to transition from OPEN to HALF-OPEN
            if self.circuit_state == "OPEN":
                current_time = asyncio.get_event_loop().time()
                if self.circuit_open_time and (
                    current_time - self.circuit_open_time >= self.recovery_timeout
                ):
                    self.circuit_state = "HALF-OPEN"
                    self.test_in_progress = False
                    logger.info("Circuit changed to HALF-OPEN, allowing test request")
                else:
                    time_remaining = (
                        self.recovery_timeout - (current_time - self.circuit_open_time)
                        if self.circuit_open_time
                        else self.recovery_timeout
                    )
                    logger.error(
                        'Query "%s" rejected - Circuit Breaker is OPEN. Time remaining: %.2f seconds',
                        sql,
                        time_remaining,
                    )
                    raise CircuitBreakerError(
                        f'Query "{sql}" rejected - Circuit Breaker is OPEN'
                    )

            # Determine if this request can proceed
            if self.circuit_state == "CLOSED":
                # Allow request in CLOSED state
                pass
            elif self.circuit_state == "HALF-OPEN":
                if not self.test_in_progress:
                    # This will be our test request
                    self.test_in_progress = True
                    is_test_request = True
                    logger.info(
                        'Selected as test request in HALF-OPEN state: "%s"', sql
                    )
                else:
                    logger.error(
                        'Query "%s" rejected - Circuit Breaker is in HALF-OPEN state and test is in progress',
                        sql,
                    )
                    raise CircuitBreakerError(
                        f'Query "{sql}" rejected - Circuit Breaker is in HALF-OPEN state'
                    )

        # Execute the query outside the lock
        try:
            result = await self.execute_query(sql)

            # Update circuit state based on success
            async with self._lock:
                if is_test_request:
                    self.circuit_state = "CLOSED"
                    self.failure_count = 0
                    self.test_in_progress = False
                    logger.info("Test request successful, circuit changed to CLOSED")
                elif self.circuit_state == "CLOSED":
                    self.failure_count = 0
                    logger.debug("Query successful, reset failure_count to 0")

            return result

        except DatabaseError as db_err:
            # Handle failure and update circuit state
            async with self._lock:
                self.failure_count += 1
                logger.critical(
                    'Query "%s" failed, failure_count=%d, circuit_state=%s',
                    sql,
                    self.failure_count,
                    self.circuit_state,
                )

                if is_test_request:
                    self.test_in_progress = False
                    self.circuit_state = "OPEN"
                    self.circuit_open_time = asyncio.get_event_loop().time()
                    logger.error("Test request failed, circuit returned to OPEN")
                elif self.failure_count >= self.failure_threshold:
                    self.circuit_state = "OPEN"
                    self.circuit_open_time = asyncio.get_event_loop().time()
                    logger.error(
                        "Failure threshold reached, circuit OPEN, waiting for %d seconds...",
                        self.recovery_timeout,
                    )
                    raise CircuitBreakerError(
                        f'Query "{sql}" rejected - Circuit Breaker threshold reached'
                    ) from db_err
                raise db_err  # Re-raise the original error if threshold not reached

    def get_stats(self, query_results: list) -> dict:
        # Return statistics dictionary
        total_requests = len(query_results)

        exception_count = 0
        for item in query_results:
            if isinstance(item, Exception):
                exception_count += 1
        successful_requests = total_requests - exception_count
        failed_requests = exception_count

        return {
            "Total_requests": {total_requests},
            "successful_requests": {successful_requests},
            "failed_requests": {failed_requests},
            "circuit_state": {self.circuit_state},
        }


async def main():
    pool = DatabasePool(pool_size=3)

    # Simulate 20 concurrent database operations
    tasks = [pool.query(f"SELECT * FROM table_({i+1})") for i in range(20)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print(pool.get_stats(results))


if __name__ == "__main__":
    asyncio.run(main())
