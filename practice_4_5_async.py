import asyncio
import random
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class CircuitBreakerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class DatabasePool:
    def __init__(self, pool_size=5, failure_threshold=3, recovery_timeout=30):
        self.pool_size = pool_size
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.semaphore = asyncio.Semaphore(self.pool_size)
        self.circuit_state = "CLOSED"
        self.failure_count = 0
        self.test_in_progress = False

        self._lock = asyncio.Lock()
        self.circuit_open_start_time = None

    async def get_connection(self, sql: str):
        async with self.semaphore:
            wait_time = random.uniform(0.5, 1.5)
            logger.debug("Executing query: %s, duration: %.1f seconds", sql, wait_time)
            await asyncio.sleep(wait_time)

            rand_num = random.random()
            if rand_num < 0.8:
                logger.critical(
                    "Database Connection Failed for query: %s, failure_count: %d, test_in_progress: %s, circuit_breaker_state: %s",
                    sql,
                    self.failure_count,
                    self.test_in_progress,
                    self.circuit_state,
                )
                raise DatabaseError("Database Connection Failed")
            else:

                logger.info(
                    'Successfully executed query: %s, resetting failure_count to 0 and circuit_breaker_state to "CLOSED"',
                    sql,
                )
                return f"Result for: {sql}"

    async def _handle_db_error(self, err):
        async with self._lock:
            self.failure_count += 1
            self.test_in_progress = False
            logger.debug(
                "Failure Count: %d, Test In Progress: %s",
                self.failure_count,
                self.test_in_progress,
            )

            if self.failure_count >= self.failure_threshold:
                self.circuit_state = "OPEN"
                self.circuit_open_start_time = datetime.now()
                logger.error(
                    'Failure count (%d) exceeds the Failure Threshold (%d), Circuit State Switched to "OPEN"',
                    self.failure_count,
                    self.failure_threshold,
                )
                raise CircuitBreakerError("Circuit Breaker Error") from err

    async def _half_open_state_execution(self, sql: str):
        if not self.test_in_progress:
            async with self._lock:
                self.test_in_progress = True

                async with asyncio.Semaphore(1):
                    try:
                        results = await self.get_connection(sql)
                        return results
                    except DatabaseError as e:
                        await self._handle_db_error(e)
                        raise

                self.test_in_progress = False
        else:
            logger.error(
                "Query (%s) rejected, circuit breaker is testing a connection in the background",
                sql,
            )
            raise CircuitBreakerError(
                "Query Rejected, a test connection is happening at the background"
            )

    async def query(self, sql: str):
        # Check Circuit Breaker State
        if self.circuit_state == "CLOSED":
            try:
                results = await self.get_connection(sql)
                async with self._lock:
                    self.failure_count = 0
                    self.test_in_progress = False
                return results
            except DatabaseError as e:
                await self._handle_db_error(e)
                raise

        elif self.circuit_state == "OPEN":
            # Check if wait time exceeds 30 seconds
            time_difference = datetime.now() - self.circuit_open_start_time
            if time_difference >= timedelta(seconds=self.recovery_timeout):
                self.circuit_state = "HALF-OPEN"
                try:
                    results = await self._half_open_state_execution(sql)
                    # Update the state to CLOSED on success
                    async with self._lock:
                        self.circuit_state = "CLOSED"
                    return results
                except DatabaseError as e:
                    logger.critical("Database Connection Error: %s", str(e))
                    raise
                except CircuitBreakerError as e:
                    logger.error("Circuit Breaker Error: %s", str(e))
                    raise
            else:
                logger.debug(
                    "Circuit is in OPEN state, waiting for another %d seconds",
                    time_difference,
                )

                remaining_time = self.recovery_timeout - time_difference.total_seconds()
                await asyncio.sleep(remaining_time)
                raise CircuitBreakerError(
                    f"Circuit is in OPEN state, waiting for another {remaining_time} seconds"
                )

        elif self.circuit_state == "HALF-OPEN":
            try:
                results = await self._half_open_state_execution(sql)
                # Update the state to CLOSED on success
                async with self._lock:
                    self.circuit_state = "CLOSED"
                return results
            except DatabaseError as e:
                logger.critical("Database Connection Error: %s", str(e))
                raise
            except CircuitBreakerError as e:
                logger.error("Circuit Breaker Error: %s", str(e))
                raise

    def get_stats(self, result: list):
        try:
            total_requests = len(result)
            failed_requests = 0

            for item in result:
                if isinstance(item, Exception):
                    failed_requests += 1

            successful_requests = total_requests - failed_requests

            return {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "circuit_state": self.circuit_state,
            }

        except TypeError as e:
            logger.error("Parameter is not a list: %s", str(e))
            raise
        except ValueError as e:
            logger.error("Value error: %s", str(e))
            raise
        except IndexError as e:
            logger.error("Index error: %s", str(e))
            raise
        except RuntimeError as e:
            logger.error("Runtime error: %s", str(e))
            raise


async def main():
    pool = DatabasePool(pool_size=3, failure_threshold=2)

    # Simulate 20 concurrent database operations
    tasks = [pool.query(f"SELECT * FROM table_({i+1})") for i in range(8)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print(pool.get_stats(results))


if __name__ == "__main__":
    asyncio.run(main())
