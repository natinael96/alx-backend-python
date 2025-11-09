#!/usr/bin/env python3
"""
Reusable query context manager for executing database queries.
"""

import sqlite3


class ExecuteQuery:
    """
    A reusable context manager that takes a query as input and executes it,
    managing both connection and query execution.
    """
    
    def __init__(self, query, params=None, db_path='users.db'):
        """
        Initialize the query context manager.
        
        Args:
            query (str): SQL query to execute
            params (tuple, optional): Parameters for the query
            db_path (str): Path to the database file
        """
        self.query = query
        self.params = params
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Enter the context manager. Opens connection and executes the query.
        
        Returns:
            list: Results from the query execution
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Execute the query with parameters if provided
        if self.params:
            self.cursor.execute(self.query, self.params)
        else:
            self.cursor.execute(self.query)
        
        # Fetch all results
        self.results = self.cursor.fetchall()
        
        return self.results
    
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


# Use the context manager with the query and parameter
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
    print(results)

