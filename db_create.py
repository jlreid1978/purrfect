import sqlite3

def initialize_database():
    conn = sqlite3.connect('users.db')  # Update with your actual database name
    cursor = conn.cursor()

    # Create 'users' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        security_question TEXT NOT NULL,
        security_answer TEXT NOT NULL,
        cat TEXT
    );
    ''')

    # Create 'food' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        type TEXT NOT NULL,
        flavor TEXT NOT NULL,
        calories REAL NOT NULL
    );
    ''')

    # Create 'cat' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        brand TEXT NOT NULL,
        type TEXT NOT NULL,
        flavor TEXT NOT NULL,
        weight REAL NOT NULL,
        calories REAL NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    );
    ''')

    conn.commit()
    conn.close()

# Initialize the database and create tables
initialize_database()
