import sqlite3
import os

# Get the absolute path to the directory where this file is located
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path for the database file
DB_PATH = os.path.join(APP_DIR, 'products.db')

def get_db_conn():
    """Returns a database connection that returns dictionary-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL,
            target_price REAL NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_product(url, target_price, email):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("INSERT INTO products (url, target_price, email) VALUES (?, ?, ?)", (url, target_price, email))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    # Convert sqlite3.Row objects to standard dictionaries to ensure
    # they work as expected in the Jinja2 template.
    return [dict(row) for row in products]

def delete_product(product_id):
    conn = get_db_conn()
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()