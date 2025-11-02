#!/usr/bin/env python3
"""
Generator function to stream rows from user_data table one by one.
"""

import mysql.connector
from mysql.connector import Error


def stream_users():
    """
    Generator function that streams rows from user_data table one by one.
    
    Yields:
        dict: Dictionary containing user_id, name, email, and age
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
            
            # Stream rows one by one using a single loop
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                yield row
                
    except Error as e:
        print(f"Error streaming users: {e}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

