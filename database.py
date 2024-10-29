import sqlite3

def initialize_database():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            ticker TEXT,
            shares REAL,
            purchase_price REAL,
            purchase_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS income (
            date TEXT,
            amount REAL,
            category TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            date TEXT,
            amount REAL,
            category TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS financial_goals (
            goal_type TEXT,
            goal_category TEXT,
            goal_amount REAL,
            progress REAL,
            PRIMARY KEY (goal_type, goal_category)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
