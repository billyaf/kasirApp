# database.py
import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "warung.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, nama_produk TEXT UNIQUE, harga_jual REAL, stok INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, total_amount REAL, user_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS transaction_details (id INTEGER PRIMARY KEY, transaction_id INTEGER, product_id INTEGER, quantity INTEGER, price_at_sale REAL)')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            change_quantity INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ('admin', hash_password('admin'), 'admin'))
    conn.commit()
    conn.close()

def log_stock_movement(cursor, product_id, change_quantity, description):
    cursor.execute("INSERT INTO stock_movements (product_id, change_quantity, description) VALUES (?, ?, ?)",
                   (product_id, change_quantity, description))

def record_transaction(total_amount, user_id, cart_details):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO transactions (total_amount, user_id) VALUES (?, ?)", (total_amount, user_id))
        transaction_id = cursor.lastrowid
        details_to_insert = [(transaction_id, pid, d['jumlah'], d['harga']) for pid, d in cart_details.items()]
        cursor.executemany("INSERT INTO transaction_details (transaction_id, product_id, quantity, price_at_sale) VALUES (?, ?, ?, ?)", details_to_insert)
        for product_id, details in cart_details.items():
            cursor.execute("UPDATE products SET stok = stok - ? WHERE id = ?", (details['jumlah'], product_id))
            log_stock_movement(cursor, product_id, -details['jumlah'], f"Penjualan (Transaksi #{transaction_id})")
        conn.commit()
        return transaction_id
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def add_new_product(name, price, stock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (nama_produk, harga_jual, stok) VALUES (?, ?, ?)", (name, price, stock))
        product_id = cursor.lastrowid
        log_stock_movement(cursor, product_id, stock, "Stok Awal Produk Baru")
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def edit_product(product_id, new_name, new_price, new_stock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stok FROM products WHERE id = ?", (product_id,))
        old_stock = cursor.fetchone()[0]
        cursor.execute("UPDATE products SET nama_produk = ?, harga_jual = ?, stok = ? WHERE id = ?", 
                       (new_name, new_price, new_stock, product_id))
        stock_change = new_stock - old_stock
        if stock_change != 0:
            log_stock_movement(cursor, product_id, stock_change, "Koreksi/Edit Stok Manual")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error edit product: {e}")
        return False
    finally:
        conn.close()

def delete_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT stok FROM products WHERE id = ?", (product_id,))
        last_stock = cursor.fetchone()[0]
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        if last_stock > 0:
            log_stock_movement(cursor, product_id, -last_stock, "Produk Dihapus dari Sistem")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error delete product: {e}")
        return False
    finally:
        conn.close()

def get_stock_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = """
    SELECT sm.timestamp, p.nama_produk, sm.change_quantity, sm.description
    FROM stock_movements sm
    LEFT JOIN products p ON sm.product_id = p.id
    ORDER BY sm.timestamp DESC
    """
    cursor.execute(query)
    history = cursor.fetchall()
    conn.close()
    return history

def add_employee(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                       (username, hash_password(password), 'kasir'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saat menghapus pengguna: {e}")
        return False
    finally:
        conn.close()

def get_all_users_and_roles():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama_produk, harga_jual, stok FROM products ORDER BY nama_produk")
    products = cursor.fetchall()
    conn.close()
    return [dict(p) for p in products]

def get_detailed_report(start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
    SELECT 
        t.timestamp,
        td.transaction_id,
        p.nama_produk,
        td.quantity,
        td.price_at_sale,
        (td.quantity * td.price_at_sale) as subtotal
    FROM transaction_details td
    JOIN transactions t ON td.transaction_id = t.id
    JOIN products p ON td.product_id = p.id
    WHERE DATE(t.timestamp) BETWEEN ? AND ?
    ORDER BY t.timestamp
    """
    cursor.execute(query, (start_date, end_date))
    report = cursor.fetchall()
    conn.close()
    return report

def get_transaction_history():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    query_header = "SELECT t.id, t.timestamp, u.username as kasir, t.total_amount FROM transactions t LEFT JOIN users u ON t.user_id = u.id ORDER BY t.timestamp DESC"
    cursor.execute(query_header)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transaction_details_by_id(transaction_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query_detail = "SELECT p.nama_produk, td.quantity, td.price_at_sale FROM transaction_details td LEFT JOIN products p ON td.product_id = p.id WHERE td.transaction_id = ?"
    cursor.execute(query_detail, (transaction_id,))
    details = cursor.fetchall()
    conn.close()
    return details