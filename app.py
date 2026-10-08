from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)

# Secret key for login session
app.secret_key = "ecomind_secret_key"


# ---------------- DATABASE CONNECTION ----------------

def get_connection():
    return sqlite3.connect("ecomind.db")


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users (username, password, points)
                VALUES (?, ?, ?)
                """,
                (username, password, 0)
            )

            connection.commit()
            connection.close()

            return """
            <h1>🎉 Registration Successful!</h1>

            <p>Your EcoMind account has been created successfully. 🌱</p>

            <a href="/login">
                <button>🔐 Login</button>
            </a>
            """

        except sqlite3.IntegrityError:

            connection.close()

            return """
            <h1>⚠️ Username Already Exists!</h1>

            <a href="/register">
                <button>📝 Try Again</button>
            </a>
            """

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, username, password, points
            FROM users
            WHERE username = ? AND password = ?
            """,
            (username, password)
        )

        user = cursor.fetchone()

        connection.close()

        if user:

            # Store username in session
            session["username"] = user[1]

            return redirect("/journey")

        else:

            return """
            <h1>❌ Invalid Username or Password</h1>

            <a href="/login">
                <button>🔐 Try Again</button>
            </a>
            """

    return render_template("login.html")


# ---------------- ECO JOURNEY ----------------

@app.route("/journey")
def journey():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT points FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    if user:
        points = user[0]
    else:
        points = 0

    return render_template(
        "journey.html",
        points=points
    )


# ---------------- COMPLETE CHALLENGE ----------------

@app.route("/complete", methods=["POST"])
def complete():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    challenge = request.form["challenge"]

    today = str(date.today())

    connection = get_connection()
    cursor = connection.cursor()

    # Check if this challenge was already completed today
    cursor.execute(
        """
        SELECT id
        FROM challenges
        WHERE username = ?
        AND challenge = ?
        AND completed_date = ?
        """,
        (username, challenge, today)
    )

    already_completed = cursor.fetchone()

    if already_completed:

        connection.close()

        return f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>EcoMind - Already Completed</title>

            <link rel="stylesheet"
                  href="/static/style.css">
        </head>

        <body>

            <h1>⚠️ Already Completed!</h1>

            <h2>🌱 {challenge}</h2>

            <h3>You already completed this challenge today.</h3>

            <p>
                Come back tomorrow to earn more Eco Points! 🌍
            </p>

            <br>

            <a href="/journey">
                <button>🌍 Back to Eco Journey</button>
            </a>

            <br><br>

            <a href="/dashboard">
                <button>📊 Dashboard</button>
            </a>

        </body>

        </html>
        """

    # Get current points
    cursor.execute(
        """
        SELECT points
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user:

        new_points = user[0] + 10

        # Add 10 points
        cursor.execute(
            """
            UPDATE users
            SET points = ?
            WHERE username = ?
            """,
            (new_points, username)
        )

        # Save completed challenge
        cursor.execute(
            """
            INSERT INTO challenges
            (username, challenge, completed_date)
            VALUES (?, ?, ?)
            """,
            (username, challenge, today)
        )

        connection.commit()

    connection.close()

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>EcoMind - Challenge Completed</title>

        <link rel="stylesheet"
              href="/static/style.css">
    </head>

    <body>

        <h1>🎉 Challenge Completed!</h1>

        <h2>✅ {challenge}</h2>

        <h3>🏆 +10 Eco Points</h3>

        <p>
            Great job! Keep building your green habits 🌱
        </p>

        <br>

        <a href="/journey">
            <button>🌍 Back to Eco Journey</button>
        </a>

        <br><br>

        <a href="/dashboard">
            <button>📊 Dashboard</button>
        </a>

    </body>

    </html>
    """


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor()

    # Get user information
    cursor.execute(
        """
        SELECT username, points
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    # Get completed challenges
    cursor.execute(
        """
        SELECT challenge, completed_date
        FROM challenges
        WHERE username = ?
        ORDER BY id DESC
        """,
        (username,)
    )

    completed_challenges = cursor.fetchall()

    connection.close()

    if user:

        username = user[0]
        points = user[1]

    else:

        points = 0

    return render_template(
        "dashboard.html",
        username=username,
        points=points,
        completed_challenges=completed_challenges
    )


# ---------------- PROFILE ----------------

@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect("/login")

    username = session["username"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT username, points
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    connection.close()

    if user:

        username = user[0]
        points = user[1]

    else:

        points = 0

    return render_template(
        "profile.html",
        username=username,
        points=points
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True)