"""Scenario: You need to process multiple large files but can't overload the system.
Requirements:
Write an async function called process_files() that:
- Takes a list of filenames and a max_concurrent parameter
- Limits concurrent operations to max_concurrent (use asyncio.Semaphore)

For each file, simulates processing by:
- Printing "Processing {filename}..."
- Waiting 2-8 seconds (random)
- Returning {"filename": filename, "size": random_size, "status": "processed"}
Where random_size is between 1000-9999 bytes

Timeout handling: If any file takes longer than 5 seconds, cancel it and mark as failed
Return results as they complete (not in original order)
Print "Completed: {filename}" as each file finishes

Function signature:
```python
async def process_files(filenames: list, max_concurrent: int = 3) -> list:
    # Your code here
    pass
```

Test case:
```python
filenames = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"]
results = await process_files(filenames, max_concurrent=2)
```
"""

import random
import asyncio


async def process_single_file(filename: str, semaphore: asyncio.Semaphore) -> dict:
    random_size = random.randint(1000, 9999)
    delay = random.uniform(2, 8)

    async with semaphore:
        try:
            print(f"Processing {filename} for {delay}s")
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            print(f"❌ {filename} was cancelled")
            raise  # Re-raise so the cancellation propagates

    return {"filename": filename, "size": random_size, "status": "processed"}


async def process_files(filenames: list, max_concurrent: int = 3) -> list:
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [
        asyncio.create_task(process_single_file(filename, semaphore))
        for filename in filenames
    ]

    results = []
    for completed_task in asyncio.as_completed(tasks):
        try:
            result = await asyncio.wait_for(completed_task, timeout=5)
            print(f"✅ Completed: {result["filename"]}")
            results.append(result)
        except asyncio.TimeoutError:
            # print("❌ A file timed out.")
            pass

    return results


async def main():
    filenames = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"]
    await process_files(filenames, max_concurrent=2)


if __name__ == "__main__":
    asyncio.run(main())

"""Unsolved Problem:
We could not successfully implement individual 5-second timeouts per task when using asyncio.as_completed() with semaphore-controlled concurrency. The combination of asyncio.wait_for() (for timeouts) + asyncio.as_completed() (for processing results as they complete) + asyncio.Semaphore (for limiting concurrency) creates internal asyncio conflicts and timing issues where tasks either get incorrectly cancelled or timeouts don't trigger when they should.
The core challenge: Making each task respect its own independent timeout while still processing results in completion order and respecting concurrency limits."""
