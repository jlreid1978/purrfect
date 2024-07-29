import sqlite3
from user import get_connection, close_connection

def add_cat(username, cat_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Retrieve current cat value for the user
        cursor.execute("SELECT cat FROM users WHERE username = ?", (username,))
        current_cats = cursor.fetchone()[0]

        # If there are existing cats, append the new cat name with a delimiter
        if current_cats:
            new_cats = current_cats + ',' + cat_name
        else:
            new_cats = cat_name

        # Update the user's cat field with the new value
        cursor.execute("UPDATE users SET cat = ? WHERE username = ?", (new_cats, username))
        conn.commit()
    finally:
        close_connection()


def remove_cat(username, cat):
    print(f'Removing {cat} for {username}')
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Retrieve the current value of the cat column
        cursor.execute("SELECT cat FROM users WHERE username = ?", (username,))
        current_cats = cursor.fetchone()[0]

        # Check if the cat is in the list of cats
        if current_cats and cat in current_cats:
            # Split the comma-separated list of cats into a list
            cats_list = current_cats.split(',')
            
            # Remove the desired cat from the list
            cats_list.remove(cat)
            
            # Join the remaining cats back into a comma-separated string
            new_cats = ','.join(cats_list)

            # Update the user's cat field with the new value
            cursor.execute("UPDATE users SET cat = ? WHERE username = ?", (new_cats, username))
            conn.commit()
            print(f'Removed {cat} from {username}')
        else:
            print(f'{cat} not found for {username}')
    finally:
        close_connection()


def get_cats(username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT cat FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    finally:
        close_connection()


def get_user_cats(username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT cat
            FROM users
            WHERE username = ?
        """, (username,))
        user_cats = cursor.fetchall()
        return user_cats
    finally:
        close_connection()


def add_food(brand, type, flavor, weight, calories):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        calories_per_oz = round(calories / weight, 1)
        cursor.execute("""
            INSERT INTO food (brand, type, flavor, calories)
            VALUES (?, ?, ?, ?)
        """, (brand, type, flavor, calories_per_oz))
        conn.commit()
    finally:
        close_connection()


def delete_food(food_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM food WHERE id = ?", (food_id,))
        conn.commit()
    finally:
        close_connection()


def get_foods():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, brand, type, flavor, calories FROM food ORDER BY brand, type, flavor")
        result = cursor.fetchall()
        return result
    finally:
        close_connection()


def get_meals_for_day(username, date):
    print(f'Getting meal for {date} - {username}')
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, brand, type, flavor, time, weight, calories, id
            FROM cat
            WHERE username = ? AND date = ?
        """, (username, date))
        meals = cursor.fetchall()
        print(f'meals - {meals}')
        return meals
    finally:
        close_connection()


def track_meal(username, cat_name, food_id, weight, selected_date):
    print(f'Tracking meal for {cat_name}, who ate {weight} oz of {food_id}')
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cat (username, name, date, time, brand, type, flavor, weight, calories)
            SELECT ?, ?, ?, time('now'), brand, type, flavor, ?, calories
            FROM food
            WHERE id = ?
        """, (username, cat_name, selected_date, weight, food_id))
        conn.commit()
    except Exception as e:
        print(f'Error inserting meal: {e}')
        raise(f'Error inserting meal: {e}')
    finally:
        close_connection()


def get_all_meals():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM cat")
        all_meals = cursor.fetchall()
        print(f'All meals in database: {all_meals}')
        return all_meals
    finally:
        close_connection()


def remove_meal(username, meal_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cat WHERE username = ? AND id = ?", (username, meal_id))
        conn.commit()
    except Exception as e:
        print(f"Error deleting meal: {e}")
    finally:
        close_connection()
