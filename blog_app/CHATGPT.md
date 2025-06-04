```
User:
----
Generate code to build a Blog website in Python that meet the following requirements. Instruct me how to run this application.
Requirements:
- Should have a nice look and easy to use.
- Types of user: Guest, Owner
- Guest can only read article, search for article
- There is only 1 owner with their information and credential stored in a text file.
- Owner can post, edit and delete articles. Login is required for owner.
- Beside the content, the article must include the posting time which is the real time recorded by the system.
- There should be a page that shows the owner's public information and contact methods.
```

Got it! Let's build a **simple blog website in Python using Flask** that meets all your requirements. We'll use basic file storage (for owner credentials) and SQLite (a lightweight database) to manage articles. Here's the breakdown:

---

### 🚀 Features

✅ **User types**:

* **Guest**: can read and search articles.
* **Owner**: can post, edit, delete articles after login.

✅ **Owner Info**: stored in a text file.

✅ **Articles**: include real posting time.

✅ **Owner public page**: shows contact information.

---

### 📝 Folder Structure

```
blog_app/
├── app.py
├── owner.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── new_article.html
│   ├── edit_article.html
│   ├── owner.html
│   └── article.html
└── static/
    └── styles.css
```

---

### 🪄 Step 1: Setup the project

```bash
mkdir blog_app
cd blog_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask
```

---

### 📦 Step 2: Create the app (`app.py`)

```python
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
```

---

### 📝 Step 3: Owner Info (`owner.txt`)

```
admin
password123
John Doe
johndoe@example.com
```

* 1st line: username
* 2nd line: password
* 3rd line: name
* 4th line: contact

---

### 🎨 Step 4: Templates

Create a `templates` folder and add these files:

#### `base.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>Simple Blog</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
  <h1><a href="{{ url_for('index') }}">My Blog</a></h1>
  <nav>
    <a href="{{ url_for('index') }}">Home</a>
    <a href="{{ url_for('owner') }}">About Owner</a>
    {% if session.get('logged_in') %}
      <a href="{{ url_for('new_article') }}">New Article</a>
      <a href="{{ url_for('logout') }}">Logout</a>
    {% else %}
      <a href="{{ url_for('login') }}">Login</a>
    {% endif %}
  </nav>
  <hr>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      {% for message in messages %}
        <p style="color:red;">{{ message }}</p>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {% block content %}{% endblock %}
</body>
</html>
```

#### `index.html`

```html
{% extends "base.html" %}
{% block content %}
  <form method="get">
    <input type="text" name="q" placeholder="Search..." value="{{ request.args.get('q', '') }}">
    <button type="submit">Search</button>
  </form>
  {% for article in articles %}
    <h2><a href="{{ url_for('article', article_id=article['id']) }}">{{ article['title'] }}</a></h2>
    <p><em>Posted on {{ article['created'] }}</em></p>
    {% if session.get('logged_in') %}
      <a href="{{ url_for('edit_article', article_id=article['id']) }}">Edit</a> |
      <a href="{{ url_for('delete_article', article_id=article['id']) }}">Delete</a>
    {% endif %}
    <hr>
  {% endfor %}
{% endblock %}
```

#### `article.html`

```html
{% extends "base.html" %}
{% block content %}
  <h2>{{ article['title'] }}</h2>
  <p><em>Posted on {{ article['created'] }}</em></p>
  <p>{{ article['content'] }}</p>
{% endblock %}
```

#### `login.html`

```html
{% extends "base.html" %}
{% block content %}
  <h2>Login</h2>
  <form method="post">
    <input type="text" name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
  </form>
{% endblock %}
```

#### `new_article.html`

```html
{% extends "base.html" %}
{% block content %}
  <h2>New Article</h2>
  <form method="post">
    <input type="text" name="title" placeholder="Title" required><br>
    <textarea name="content" placeholder="Content" required></textarea><br>
    <button type="submit">Post</button>
  </form>
{% endblock %}
```

#### `edit_article.html`

```html
{% extends "base.html" %}
{% block content %}
  <h2>Edit Article</h2>
  <form method="post">
    <input type="text" name="title" value="{{ article['title'] }}" required><br>
    <textarea name="content" required>{{ article['content'] }}</textarea><br>
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

#### `owner.html`

```html
{% extends "base.html" %}
{% block content %}
  <h2>About the Owner</h2>
  <p>Name: {{ owner.name }}</p>
  <p>Contact: {{ owner.contact }}</p>
{% endblock %}
```

---

### 🎨 Step 5: Add Styles

Create `static/styles.css`:

```css
body { font-family: Arial, sans-serif; margin: 20px; }
nav a { margin: 0 10px; }
input, textarea { width: 300px; margin: 5px 0; }
textarea { height: 150px; }
```

---

### 💡 Step 6: Running the application

1. **Activate your virtual environment:**

   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Run the app:**

   ```bash
   python app.py
   ```
3. Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

**✅ That's it!**
You now have a fully functional blog website with guest and owner roles, real posting times, and an owner info page. Let me know if you'd like help extending this further (e.g., deploying to the cloud, adding user registration, etc.)!

---
---
---
```
User:
----
The article does not show line break
```

Ah, good catch! By default, HTML ignores line breaks in text. To **preserve line breaks in the article content**, you can update how the content is displayed in the `article.html` template.

Let’s tweak it:

---

### 🛠 Updated `article.html`:

```html
{% extends "base.html" %}
{% block content %}
  <h2>{{ article['title'] }}</h2>
  <p><em>Posted on {{ article['created'] }}</em></p>
  <p style="white-space: pre-line;">{{ article['content'] }}</p>
{% endblock %}
```

The key addition is:

```html
<p style="white-space: pre-line;">{{ article['content'] }}</p>
```

* `white-space: pre-line;` tells the browser to treat line breaks (`\n`) in the text as actual breaks when rendering.

---

### 🔄 Where to apply it?

If there are **other templates** (like `index.html` snippets) where article content is shown directly, you might also want to wrap them with the same `style="white-space: pre-line;"` or a CSS class.

---

Let me know if you’d like me to help extend this to other pages or add any other tweaks! 🚀
