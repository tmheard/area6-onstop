from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
from datetime import date
import sqlite3

app = Flask(__name__)
app.secret_key = "yoursecretkey"

# Inject today's date into all templates
@app.context_processor
def inject_today():
    return {"today": date.today()}

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect("onstop.db")
    conn.row_factory = sqlite3.Row
    return conn

# Login setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Dummy user model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {"admin": User(1, "admin", "password")}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("index"))
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return render_template("dashboard.html")

@app.route("/closures", methods=["GET", "POST"])
@login_required
def closures():
    conn = get_db_connection()
    if request.method == "POST":
        store = request.form["store"]
        closure_date = request.form["closure_date"]
        time_closed = request.form["time_closed"]
        time_opened = request.form["time_opened"]
        reason = request.form["reason"]
        conn.execute(
            "INSERT INTO closures (store, closure_date, time_closed, time_opened, reason) VALUES (?, ?, ?, ?, ?)",
            (store, closure_date, time_closed, time_opened, reason),
        )
        conn.commit()
        return redirect(url_for("closures"))

    data = conn.execute("SELECT * FROM closures").fetchall()
    conn.close()
    return render_template("closures.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
