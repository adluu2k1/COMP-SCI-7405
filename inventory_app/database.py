import sqlite3

def connect_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    # Create tables if they don’t exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            date TEXT,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
        )
    ''')
    conn.commit()
    return conn

def add_stock(name, quantity, price):
    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO stock (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

def update_stock(stock_id, name, quantity, price):
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE stock SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, stock_id))
    conn.commit()
    conn.close()

def delete_stock(stock_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM stock WHERE id=?", (stock_id,))
    conn.commit()
    conn.close()

def get_all_stock():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM stock")
    data = c.fetchall()
    conn.close()
    return data

def add_order(stock_id, quantity, date):
    conn = connect_db()
    c = conn.cursor()
    # Get stock price
    c.execute("SELECT price, quantity FROM stock WHERE id=?", (stock_id,))
    stock = c.fetchone()
    if stock:
        price, stock_qty = stock
        if stock_qty >= quantity:
            total_price = price * quantity
            c.execute("INSERT INTO orders (stock_id, quantity, total_price, date) VALUES (?, ?, ?, ?)",
                      (stock_id, quantity, total_price, date))
            # Update stock
            new_qty = stock_qty - quantity
            c.execute("UPDATE stock SET quantity=? WHERE id=?", (new_qty, stock_id))
            conn.commit()
        else:
            raise Exception("Not enough stock!")
    else:
        raise Exception("Stock not found!")
    conn.close()

def get_all_orders():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        SELECT orders.id, stock.name, orders.quantity, orders.total_price, orders.date
        FROM orders
        JOIN stock ON orders.stock_id = stock.id
    ''')
    data = c.fetchall()
    conn.close()
    return data
