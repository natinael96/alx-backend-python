#!/usr/bin/env python3
"""
Lazy pagination generator to fetch users in pages from the database.
"""

import seed


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database.
    
    Args:
        page_size (int): Number of users to fetch per page
        offset (int): Number of users to skip
    
    Returns:
        list: List of dictionaries containing user data
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator function that lazily fetches paginated data from users database.
    Only fetches the next page when needed.
    
    Args:
        page_size (int): Number of users to fetch per page
    
    Yields:
        list: List of dictionaries containing user data for each page
    """
    offset = 0
    
    # Single loop to fetch pages lazily
    while True:
        page = paginate_users(page_size, offset)
        
        # If no more pages, stop
        if not page:
            break
        
        yield page
        
        # Move to next page
        offset += page_size

