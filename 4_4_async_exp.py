"""
# Problem: Async API Client with Retry Logic

## Scenario: You're building an API client that needs to handle unreliable services.

## Requirements: Write an async function called `fetch_with_retry()` that:
1. Takes `url`, `max_retries=3`, `base_delay=1.0` parameters
2. Simulates API calls with:
    - 40% chance of `ConnectionError`
    - 30% chance of `TimeoutError`
    - 30% chance of success (returns `f"Data from {url}"`)

3. Exponential backoff: `Wait base_delay * (2 ** attempt - 1)` seconds between retries
4. Give up after `max_retries` attempts and raise the last exception
5. Log attempts: Print `"Attempt {attempt} for {url}"` before each try
6. Write a main function that fetches 5 URLs concurrently, each with retry logic

Bonus: Handle the case where different URLs might need different retry strategies."""

import random
import logging
import asyncio

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def fetch_with_retry(url: str, max_retries: int = 3, base_delay: float = 1.0):

    last_exception = None

    for attempt in range(1, max_retries + 1):
        logger.debug("Attempt %d for %s", attempt, url)
        try:
            rand_num = random.uniform(0, 1)
            if rand_num < 0.4:
                raise ConnectionError("❌ Connection Error")
            elif rand_num < 0.7:
                raise asyncio.TimeoutError("❌ A timeout error has occurred")
            else:
                return f"✅ Data from {url}"
        except (ConnectionError, asyncio.TimeoutError) as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(base_delay * (2**attempt - 1))

    raise last_exception


async def main():
    urls = ["url1", "url2", "url3", "url4", "url5"]

    tasks = [asyncio.create_task(fetch_with_retry(url)) for url in urls]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    logger.info(dict(zip(urls, results)))


if __name__ == "__main__":
    asyncio.run(main())
