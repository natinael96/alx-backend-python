#!/usr/bin/env python3
"""
Custom class-based context manager for database connections.
"""

import sqlite3


class DatabaseConnection:
    """
    A context manager class that handles opening and closing database connections automatically.
    """
    
    def __init__(self, db_path='users.db'):
        """
        Initialize the database connection context manager.
        
        Args:
            db_path (str): Path to the database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """
        Enter the context manager. Opens the database connection.
        
        Returns:
            DatabaseConnection: The context manager instance
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager. Closes the database connection.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        
        Returns:
            bool: False to propagate exceptions, True to suppress them
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return False  # Propagate exceptions if any occurred


# Use the context manager with the with statement
with DatabaseConnection() as db:
    db.cursor.execute("SELECT * FROM users")
    results = db.cursor.fetchall()
    print(results)

