from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret_key'  # Change to something secure!

ORDERS_FILE = 'orders.json'
SETTINGS_FILE = 'settings.json'
USERS_FILE = 'users.txt'

# Helpers for JSON file I/O
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'num_tables': 0, 'menu': []}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open(USERS_FILE, 'r') as f:
            for line in f:
                if ',' not in line:
                    continue  # skip malformed lines
                user, pw = line.strip().split(',', 1)
                if username == user and password == pw:
                    session['username'] = username
                    return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    orders = load_orders()
    return render_template('index.html', orders=orders)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_order():
    settings = load_settings()
    if request.method == 'POST':
        table = request.form['table']

        # Extract quantities
        quantities_dict = {}
        for key, value in request.form.items():
            if key.startswith('quantities['):
                dish_name = key[len('quantities['):-1]
                quantities_dict[dish_name] = int(value)

        # Build dishes dict and calculate total
        dishes = {}
        total = 0
        for item in settings['menu']:
            dish_name = item['name']
            qty = quantities_dict.get(dish_name, 0)
            if qty > 0:
                dishes[dish_name] = {
                    'quantity': qty,
                    'price': item['price']
                }
                total += qty * item['price']

        order = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'table': table,
            'dishes': dishes,
            'total': total,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'paid': False
        }

        orders = load_orders()
        orders.append(order)
        save_orders(orders)
        return redirect(url_for('index'))
    return render_template('order_form.html', settings=settings)

@app.route('/edit/<order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    orders = load_orders()
    order = next((o for o in orders if o['id'] == order_id), None)
    settings = load_settings()
    if request.method == 'POST':
        table = request.form['table']

        quantities_dict = {}
        for key, value in request.form.items():
            if key.startswith('quantities['):
                dish_name = key[len('quantities['):-1]
                quantities_dict[dish_name] = int(value)

        dishes = {}
        total = 0
        for item in settings['menu']:
            dish_name = item['name']
            qty = quantities_dict.get(dish_name, 0)
            if qty > 0:
                dishes[dish_name] = {
                    'quantity': qty,
                    'price': item['price']
                }
                total += qty * item['price']

        order['table'] = table
        order['dishes'] = dishes
        order['total'] = total
        save_orders(orders)
        return redirect(url_for('index'))
    return render_template('order_form.html', order=order, settings=settings)

@app.route('/delete/<order_id>')
@login_required
def delete_order(order_id):
    orders = load_orders()
    orders = [o for o in orders if o['id'] != order_id]
    save_orders(orders)
    return redirect(url_for('index'))

@app.route('/mark_paid/<order_id>')
@login_required
def mark_paid(order_id):
    orders = load_orders()
    for o in orders:
        if o['id'] == order_id:
            o['paid'] = True
            break
    save_orders(orders)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings = load_settings()
    if request.method == 'POST':
        num_tables = int(request.form['num_tables'])
        menu_str = request.form['menu']
        menu_items = []
        for item in menu_str.split(','):
            name_price = item.strip().split(':')
            if len(name_price) == 2:
                name, price = name_price
                menu_items.append({'name': name.strip(), 'price': float(price.strip())})
        settings = {
            'num_tables': num_tables,
            'menu': menu_items
        }
        save_settings(settings)
        return redirect(url_for('index'))
    menu_str = ', '.join([f"{item['name']}:{item['price']}" for item in settings['menu']])
    return render_template('settings.html', settings=settings, menu_str=menu_str)

if __name__ == '__main__':
    app.run(debug=True)
