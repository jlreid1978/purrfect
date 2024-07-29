import bcrypt
import re
import sqlite3
import threading

# Create a thread-local storage for the SQLite connection
local = threading.local()

# Functions to connect to the SQLite database
def get_cursor():
    conn = get_connection()
    return conn.cursor()

def get_connection():
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('users.db')
    return local.conn

def close_connection():
    if hasattr(local, 'conn'):
        local.conn.close()
        del local.conn


def get_current_user(session):
    if 'username' in session:
        return {'is_authenticated': True, 'username': session['username'], 'name': session['name']}
    return {'is_authenticated': False, 'username': None, 'name': None}

# Function to register new user
def register_user(name, username, email, password, security_question, security_answer):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if not is_valid_password(password):
            return "Password must be 8 characters and contain one of the following: Upper Case, Number, and Symbol"
        if user_exists(username, email, conn, cursor):
            return "Username or Email already exists"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        security_answer_hash = bcrypt.hashpw(security_answer.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (name, username, email, password_hash, security_question, security_answer) VALUES (?, ?, ?, ?, ?, ?)", 
                       (name, username, email, password_hash, security_question, security_answer_hash))
        conn.commit()
        return "Registration successful"
    except sqlite3.IntegrityError:
        return "Error in registration process"
    finally:
        close_connection()



# Function to check if username or email already exists
def user_exists(username, email, conn=None, cursor=None):
    conn = conn or get_connection()
    cursor = cursor or conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username=? OR email=?", (username, email))
    result = cursor.fetchone()
    return result is not None

# Function to validate password entries and changes
def is_valid_password(password):
    upper_regex = re.compile(r'[A-Z]')
    digit_regex = re.compile(r'\d')
    symbol_regex = re.compile(r'[!@#$%^&*()_+{}[\]:;<>,.?/~]')
    has_uppercase = bool(upper_regex.search(password))
    has_digit = bool(digit_regex.search(password))
    has_symbol = bool(symbol_regex.search(password))
    length_valid = len(password) >= 8
    return has_uppercase and has_digit and has_symbol and length_valid

def verify_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            stored_hash = result[0]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True
    finally:
        close_connection()
    return False


# Function to delete user
def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    close_connection()

# Function to get name from database
def get_name(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return result[0]
    else:
        return None


def verify_security_answer(username, security_answer):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT security_answer FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            stored_answer_hash = result[0]
            if bcrypt.checkpw(security_answer.encode('utf-8'), stored_answer_hash.encode('utf-8')):
                return True
    finally:
        close_connection()
    return False


def change_password(username, new_password):
    print(f'user function {username} - {new_password}')
    if not is_valid_password(new_password):
        raise ValueError("Password must be 8 characters and contain one of the following: Upper Case, Number, and Symbol")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, username))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        close_connection()


def update_email(username, new_email):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
        conn.commit()
    finally:
        close_connection()


def get_user_info(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return {
            'name': result[0],
            'email': result[1],
            'username': result[2],
            'password_hash': result[3],
            'security_question': result[4],
            'security_answer': result[5],
            'is_authenticated': True
        }
    return None

def get_user_info(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return {
            'name': result[1],
            'username': result[2],
            'email': result[3],
            'password_hash': result[4],
            'security_question': result[5],
            'security_answer': result[6],
            'is_authenticated': True
        }
    return None


def get_forgot_info(username, email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return {
            'name': result[1],
            'username': result[2],
            'email': result[3],
            'password_hash': result[4],
            'security_question': result[5],
            'security_answer': result[6],
            'is_authenticated': True
        }
    return None
