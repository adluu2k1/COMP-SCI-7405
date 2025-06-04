from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))  # plaintext for simplicity, should be hashed
    role = db.Column(db.String(20))  # "customer" or "staff"

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)

class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    borrow_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html', user_role=session.get('role'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('index'))

# Search Books (open to everyone)
@app.route('/search', methods=['GET', 'POST'])
def search():
    books = []
    if request.method == 'POST':
        search_term = request.form['search_term']
        books = Book.query.filter(Book.title.contains(search_term)).all()
    return render_template('search.html', books=books, user_role=session.get('role'))

# Borrow Book (customers only)
@app.route('/borrow/<int:book_id>', methods=['GET', 'POST'])
def borrow(book_id):
    if session.get('role') != 'customer':
        flash('Access denied. Customers only.')
        return redirect(url_for('index'))

    book = Book.query.get(book_id)
    if request.method == 'POST':
        customer_name = session['username']
        if book and book.available:
            record = BorrowRecord(customer_name=customer_name, book_id=book.id)
            book.available = False
            db.session.add(record)
            db.session.commit()
            flash('Book borrowed successfully!')
            return redirect(url_for('index'))
        else:
            flash('Book is not available.')
    return render_template('borrow.html', book=book, user_role=session.get('role'))

# Return Book (customers only)
@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if session.get('role') != 'customer':
        flash('Access denied. Customers only.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        record = BorrowRecord.query.filter_by(book_id=book_id, customer_name=session['username'], return_date=None).first()
        if record:
            record.return_date = datetime.datetime.utcnow()
            book = Book.query.get(book_id)
            book.available = True
            db.session.commit()
            flash('Book returned successfully!')
        else:
            flash('No active borrow record found for this book.')
    return render_template('return.html', user_role=session.get('role'))

# View Receipts (customers only)
@app.route('/receipts')
def receipts():
    if session.get('role') != 'customer':
        flash('Access denied. Customers only.')
        return redirect(url_for('index'))

    records = BorrowRecord.query.filter_by(customer_name=session['username']).all()
    return render_template('receipts.html', records=records, user_role=session.get('role'))

# Staff: Add Book
@app.route('/staff', methods=['GET', 'POST'])
def staff():
    if session.get('role') != 'staff':
        flash('Access denied. Staff only.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book = Book(title=title, author=author, available=True)
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!')
    return render_template('staff.html', user_role=session.get('role'))

# Staff: Manage Inventory
@app.route('/manage_books')
def manage_books():
    if session.get('role') != 'staff':
        flash('Access denied. Staff only.')
        return redirect(url_for('index'))

    books = Book.query.all()
    return render_template('manage_books.html', books=books, user_role=session.get('role'))

# Initialize DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add default users if they don’t exist
        if not User.query.filter_by(username='customer1').first():
            db.session.add(User(username='customer1', password='pass', role='customer'))
        if not User.query.filter_by(username='staff1').first():
            db.session.add(User(username='staff1', password='pass', role='staff'))
        db.session.commit()
    app.run(debug=True)
