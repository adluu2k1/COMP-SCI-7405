from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = "blog.db"
OWNER_INFO_FILE = "owner.txt"

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_owner_info():
    with open(OWNER_INFO_FILE, "r") as f:
        lines = f.read().splitlines()
    return {"username": lines[0], "password": lines[1], "name": lines[2], "contact": lines[3]}

# Routes
@app.route("/")
def index():
    query = request.args.get("q")
    conn = get_db_connection()
    if query:
        articles = conn.execute("SELECT * FROM articles WHERE title LIKE ? OR content LIKE ?", 
                                ('%'+query+'%', '%'+query+'%')).fetchall()
    else:
        articles = conn.execute("SELECT * FROM articles ORDER BY created DESC").fetchall()
    conn.close()
    return render_template("index.html", articles=articles)

@app.route("/article/<int:article_id>")
def article(article_id):
    conn = get_db_connection()
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    conn.close()
    if article is None:
        return "Article not found", 404
    return render_template("article.html", article=article)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        owner = get_owner_info()
        if username == owner["username"] and password == owner["password"]:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))

@app.route("/new", methods=["GET", "POST"])
def new_article():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        conn.execute("INSERT INTO articles (title, content, created) VALUES (?, ?, ?)",
                     (title, content, created))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("new_article.html")

@app.route("/edit/<int:article_id>", methods=["GET", "POST"])
def edit_article(article_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    conn = get_db_connection()
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        conn.execute("UPDATE articles SET title = ?, content = ? WHERE id = ?",
                     (title, content, article_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("edit_article.html", article=article)

@app.route("/delete/<int:article_id>")
def delete_article(article_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/owner")
def owner():
    owner = get_owner_info()
    return render_template("owner.html", owner=owner)

if __name__ == "__main__":
    # Initialize database if needed
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created TEXT NOT NULL
    )
    """)
    conn.close()
    app.run(debug=True)
