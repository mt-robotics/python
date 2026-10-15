"""Problem: Async Web Scraper with Error Handling
Scenario: You're building a web scraper that needs to handle unreliable websites.
Requirements:
Write an async function called scrape_websites() that:

Takes a list of URLs as input
For each URL, simulates fetching by:

Printing "Scraping {url}..."
Waiting 1-3 seconds (random)
30% chance of failure - raise ConnectionError(f"Failed to connect to {url}")
70% chance of success - return f"Content from {url}"


Handle errors gracefully - failed URLs should not crash the entire operation
Return a dictionary with two keys:

"successful": list of successful results
"failed": list of failed URLs


All requests should run concurrently

## Expected output format:
{
    "successful": ["Content from url1", "Content from url3"],
    "failed": ["url2", "url4"]
}"""

import random
import asyncio


async def scrape_websites(urls: list) -> dict:
    success_urls = []
    fail_urls = []

    async def scrape_single_website(url: str) -> str:
        delay = random.uniform(1, 3)
        print(f"Scraping {url}...")
        await asyncio.sleep(delay)

        if random.random() < 0.3:  # 30% chance (0.0 to 0.3)
            raise ConnectionError(f"Failed to connect to {url}")
        else:  # 70% chance (0.3 to 1.0)
            return f"Content from {url}"

    tasks = [asyncio.create_task(scrape_single_website(url)) for url in urls]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            fail_urls.append(urls[i])
        else:
            success_urls.append(result)

    return {"successful": success_urls, "failed": fail_urls}


async def main():
    urls = ["url1", "url2", "url3", "url4", "url5"]
    result = await scrape_websites(urls)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
