# Python Generators 0x00

This project demonstrates database setup and data seeding using Python and MySQL.

## Files

- `seed.py`: Script to set up MySQL database and populate with user data
- `user_data.csv`: Sample user data in CSV format
- `0-main.py`: Main script to run the seeding process

## Requirements

- Python 3.x
- MySQL Server
- mysql-connector-python library

## Installation

Install the required dependency:
```bash
pip install mysql-connector-python
```

## Database Configuration

Update the database connection settings in `seed.py`:
- host: 'localhost'
- user: 'root'
- password: '' (update with your MySQL password)

## Usage

Run the main script:
```bash
python3 0-main.py
```

## Database Schema

**Database:** ALX_prodev

**Table:** user_data
- `user_id` (VARCHAR(36), PRIMARY KEY, INDEXED)
- `name` (VARCHAR(255), NOT NULL)
- `email` (VARCHAR(255), NOT NULL)
- `age` (DECIMAL(10, 2), NOT NULL)

