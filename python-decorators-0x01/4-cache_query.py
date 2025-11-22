#!/usr/bin/env python3
"""
Decorator to cache database query results.
"""

import time
import sqlite3
import functools


query_cache = {}


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


def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    If the query has been executed before, returns the cached result instead of executing again.
    
    Args:
        func: The function to be decorated
    
    Returns:
        wrapper: The wrapped function that caches query results
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        # Extract query from kwargs or args
        query = kwargs.get('query', None)
        if query is None and args:
            # If query is passed as positional argument, check first arg after conn
            query = args[0] if args else None
        
        # Check if query result is in cache
        if query in query_cache:
            return query_cache[query]
        
        # Execute the function and get the result
        result = func(conn, *args, **kwargs)
        
        # Cache the result
        query_cache[query] = result
        
        return result
    
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")

