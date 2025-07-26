from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect("demo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, role TEXT)")
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return '''
        <h2>SQLi & RCE Demo</h2>
        <ul>
            <li><a href="/user?id=1">User Lookup</a></li>
            <li><a href="/run">Run Command</a></li>
        </ul>
    '''

@app.route("/user")
def user_lookup():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect("demo.db")
    cursor = conn.cursor()
    # SQL Injection vulnerability
    cursor.execute(f"SELECT name, role FROM users WHERE id = {user_id}")
    row = cursor.fetchone()
    conn.close()

    if row:
        return f"<p>User: {row[0]}<br>Role: {row[1]}</p>"
    return "User not found"

@app.route("/run", methods=["GET", "POST"])
def run_cmd():
    if request.method == "POST":
        # Remote code execution vulnerability
        pass
    return '''
        <form method="post">
            <input name="cmd" placeholder="Enter command"/>
            <input type="submit" value="Execute"/>
        </form>
    '''

if __name__ == "__main__":
    init_db()
    # Use environment variable to control debug mode in production
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)