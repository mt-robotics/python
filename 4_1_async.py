"""Scenario: You're building a system that needs to fetch user data from multiple sources concurrently.
Requirements:
Write an async function called fetch_user_data() that:

Takes a list of user IDs as input
For each user ID, simulates fetching data by:

Printing "Fetching user {id}..."
Waiting for a random delay between 0.5 and 2.0 seconds
Returning a dictionary: {"id": user_id, "name": f"User{user_id}", "status": "active"}


All fetches should happen concurrently (not one after another)
Returns a list of all user data dictionaries
The function should complete in roughly the time of the slowest fetch (not the sum of all fetches)
"""

import random
import asyncio


async def fetch_user_data(user_ids: list) -> list:
    async def fetch_single_user(user_id: int) -> dict:
        delay = random.uniform(0.5, 2.0)
        print(f"Fetching user {user_id}...")
        await asyncio.sleep(delay)
        return {"id": user_id, "name": f"User{user_id}", "status": "active"}

    tasks = [fetch_single_user(id) for id in user_ids]
    results = await asyncio.gather(*tasks)
    return results


async def main():
    user_ids = [101, 102, 103]
    results = await fetch_user_data(user_ids)
    print("Results: ", results)


if __name__ == "__main__":
    asyncio.run(main())
