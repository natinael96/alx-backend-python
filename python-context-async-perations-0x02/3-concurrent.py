#!/usr/bin/env python3
"""
Concurrent asynchronous database queries using asyncio.
"""

import asyncio
import aiosqlite


async def async_fetch_users():
    """
    Asynchronous function that fetches all users from the database.
    
    Returns:
        list: List of all users
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            return results


async def async_fetch_older_users():
    """
    Asynchronous function that fetches users older than 40 from the database.
    
    Returns:
        list: List of users older than 40
    """
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            return results


async def fetch_concurrently():
    """
    Executes both async fetch functions concurrently using asyncio.gather.
    
    Returns:
        tuple: Results from both queries
    """
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    return results


# Run the concurrent fetch
if __name__ == "__main__":
    all_users, older_users = asyncio.run(fetch_concurrently())
    print("All users:", all_users)
    print("Users older than 40:", older_users)

