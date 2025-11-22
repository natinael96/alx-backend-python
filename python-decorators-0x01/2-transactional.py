#!/usr/bin/env python3
"""
Decorator to manage database transactions.
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


def transactional(func):
    """
    Decorator that manages database transactions by automatically committing or rolling back changes.
    If the function raises an error, rollback; otherwise commit the transaction.
    
    Args:
        func: The function to be decorated
    
    Returns:
        wrapper: The wrapped function that handles transactions
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            # If successful, commit the transaction
            conn.commit()
            return result
        except Exception as e:
            # If an error occurs, rollback the transaction
            conn.rollback()
            # Re-raise the exception
            raise
    
    return wrapper


@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))


# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')

