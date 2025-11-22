#!/usr/bin/env python3
"""
Decorator to retry database operations on failure.
"""

import time
import sqlite3
import functools


def with_db_connection(func):
    """
    Decorator that automatically opens a database connection, passes it to the function,
    and closes it afterward.
    
    Args:
        func: The function to be decorated
    
    Returns:
        wrapper: The wrapped function that handles database connections
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection as first argument to the function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close the connection, even if an error occurs
            conn.close()
    
    return wrapper


def retry_on_failure(retries=3, delay=2):
    """
    Decorator factory that creates a decorator to retry database operations if they fail.
    
    Args:
        retries (int): Number of times to retry the function (default: 3)
        delay (int): Delay in seconds between retries (default: 2)
    
    Returns:
        decorator: A decorator that retries the function on failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # Try to execute the function up to 'retries' times
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    # If this is not the last attempt, wait before retrying
                    if attempt < retries - 1:
                        time.sleep(delay)
                    # If this is the last attempt, the exception will be raised below
            
            # If all retries failed, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


# Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)

