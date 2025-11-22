#!/usr/bin/env python3
"""
Memory-efficient average age calculation using generators.
"""

import mysql.connector
from mysql.connector import Error


def stream_user_ages():
    """
    Generator function that yields user ages one by one from the database.
    
    Yields:
        float: Age of each user
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
            cursor = connection.cursor()
            
            # Execute query to fetch only ages (more memory efficient)
            cursor.execute("SELECT age FROM user_data")
            
            # Stream ages one by one using a single loop
            while True:
                row = cursor.fetchone()
                if row is None:
                    break
                # Convert DECIMAL to float and yield
                yield float(row[0])
                
    except Error as e:
        print(f"Error streaming user ages: {e}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def calculate_average_age():
    """
    Calculates the average age of users using the generator.
    This approach is memory-efficient as it doesn't load all data into memory.
    """
    total_age = 0
    count = 0
    
    # Loop through ages using the generator (Loop 1)
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate and print average
    if count > 0:
        average_age = total_age / count
        print(f"Average age of users: {average_age}")
    else:
        print("Average age of users: 0")


if __name__ == "__main__":
    calculate_average_age()

