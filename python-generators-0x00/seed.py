#!/usr/bin/env python3
"""
Seed script to set up MySQL database and populate with user data.
"""

import mysql.connector
from mysql.connector import Error
import csv
import os


def connect_db():
    """
    Connects to the MySQL database server.
    
    Returns:
        connection: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL server: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")


def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    
    Returns:
        connection: MySQL connection object or None if connection fails
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None


def create_table(connection):
    """
    Creates the user_data table if it does not exist with the required fields.
    
    Args:
        connection: MySQL connection object
    """
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) NOT NULL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(10, 2) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data from CSV file into the database if it does not exist.
    
    Args:
        connection: MySQL connection object
        csv_file: Path to the CSV file containing user data
    """
    try:
        if not os.path.exists(csv_file):
            print(f"Error: CSV file '{csv_file}' not found")
            return
        
        cursor = connection.cursor()
        inserted_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                user_id = row['user_id'].strip()
                name = row['name'].strip()
                email = row['email'].strip()
                age = row['age'].strip()
                
                # Check if record already exists
                check_query = "SELECT COUNT(*) FROM user_data WHERE user_id = %s"
                cursor.execute(check_query, (user_id,))
                exists = cursor.fetchone()[0]
                
                if not exists:
                    insert_query = """
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (user_id, name, email, age))
                    inserted_count += 1
                else:
                    skipped_count += 1
        
        connection.commit()
        cursor.close()
        print(f"Data insertion completed: {inserted_count} inserted, {skipped_count} skipped")
    except Error as e:
        print(f"Error inserting data: {e}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

