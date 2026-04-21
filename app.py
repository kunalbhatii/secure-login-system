from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"
bcrypt = Bcrypt(app)

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("users.db")

# ---------- PASSWORD CHECK ----------
def is_strong(password):
    return (
        len(password) >= 6 and
        re.search("[A-Z]", password) and
        re.search("[0-9]", password)
    )

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not is_strong(password):
            flash("Weak password! Use 6 chars, 1 capital, 1 number")
            return redirect("/register")

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            flash("Registered successfully!")
            return redirect("/login_secure")
        except:
            flash("User already exists!")
        finally:
            conn.close()

    return render_template("register.html")

# ---------- VULNERABLE LOGIN ----------
@app.route("/login_vulnerable", methods=["GET", "POST"])
def login_vulnerable():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cur.execute(query)

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            flash("Invalid Login")

    return render_template("login_vulnerable.html")

# ---------- SECURE LOGIN ----------
@app.route("/login_secure", methods=["GET", "POST"])
def login_secure():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and bcrypt.check_password_hash(user[2], password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            flash("Invalid Login")

    return render_template("login_secure.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect("/login_secure")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)