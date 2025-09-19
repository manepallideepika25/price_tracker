import sqlite3

DATABASE_FILE = "C:\\Users\\deepi\\OneDrive\\Desktop\\price tracking system\\price_tracking_app\\products.db"

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the products table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute(    '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            threshold_price REAL NOT NULL,
            current_price REAL,
            last_checked TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_product(url, threshold_price):
    """Adds a new product to the database."""
    conn = get_db_connection()
    conn.execute('INSERT INTO products (url, threshold_price) VALUES (?, ?)', (url, threshold_price))
    conn.commit()
    conn.close()

def delete_product(product_id):
    """Deletes a product from the database."""
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def get_all_products():
    """Retrieves all products from the database."""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return products

def update_price(product_id, price):
    """Updates the price of a product."""
    conn = get_db_connection()
    conn.execute('UPDATE products SET current_price = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?', (price, product_id))
    conn.commit()
    conn.close()
