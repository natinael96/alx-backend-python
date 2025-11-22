#!/usr/bin/env python3
"""
Batch processing functions to fetch and process users in batches.
"""

import mysql.connector
from mysql.connector import Error


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from user_data table in batches.
    
    Args:
        batch_size (int): Number of rows to fetch per batch
    
    Yields:
        list: List of dictionaries containing user data for each batch
    """
    connection = None
    cursor = None
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        
        if connection.is_connected():
            # Create a cursor with dictionary=True to get results as dicts
            cursor = connection.cursor(dictionary=True)
            
            # Execute the query to fetch all users
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            
            # Fetch rows in batches using a single loop
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                yield batch
                
    except Error as e:
        print(f"Error streaming users in batches: {e}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users and filters those over age 25.
    
    Args:
        batch_size (int): Number of rows to fetch per batch
    """
    # Loop through batches (Loop 1)
    for batch in stream_users_in_batches(batch_size):
        # Filter and print users over age 25 (Loop 2)
        for user in batch:
            # Convert age to float for comparison (age is DECIMAL in DB)
            age = float(user['age'])
            if age > 25:
                print(user)

