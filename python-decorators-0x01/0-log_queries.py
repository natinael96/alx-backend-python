#!/usr/bin/env python3
"""
Decorator to log SQL queries before execution.
"""

import sqlite3
import functools


def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    
    Args:
        func: The function to be decorated
    
    Returns:
        wrapper: The wrapped function that logs queries
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from kwargs or args
        query = kwargs.get('query', None)
        if query is None and args:
            # If query is passed as positional argument, check first arg
            query = args[0] if args else None
        
        # Log the query if it exists
        if query:
            print(f"Executing query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")

