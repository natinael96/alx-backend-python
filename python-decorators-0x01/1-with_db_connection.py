#!/usr/bin/env python3
"""
Decorator to automatically handle database connections.
"""

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


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)

