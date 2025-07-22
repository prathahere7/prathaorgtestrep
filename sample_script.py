from flask import Flask, request, render_template_string
import sqlite3
import subprocess

app = Flask(__name__)

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect('vulndb.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return '''
        <h2>Welcome to Vulnerable App</h2>
        <ul>
            <li><a href="/register">Register</a></li>
            <li><a href="/login">Login</a></li>
            <li><a href="/user?id=1">User Info (SQLi)</a></li>
            <li><a href="/exec">Run OS Command (RCE)</a></li>
        </ul>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        passwd = request.form['password']
        email = request.form['email']

        conn = sqlite3.connect('vulndb.db')
        cur = conn.cursor()

        # SQL Injection vulnerability
        query = f"INSERT INTO users (username, password, email) VALUES ('{uname}', '{passwd}', '{email}')"
        cur.execute(query)
        conn.commit()
        conn.close()

        return "Registration successful"
    
    return '''
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password"><br>
            Email: <input name="email"><br>
            <input type="submit" value="Register">
        </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    uname = request.form.get('username')
    passwd = request.form.get('password')

    conn = sqlite3.connect('vulndb.db')
    cur = conn.cursor()
    # SQLi vulnerability
    sql = f"SELECT * FROM users WHERE username = '{uname}' AND password = '{passwd}'"
    cur.execute(sql)
    user = cur.fetchone()
    conn.close()

    if user:
        return f"Welcome {uname}"
    return "Login failed"

@app.route('/user')
def user_info():
    uid = request.args.get('id', '1')
    conn = sqlite3.connect('vulndb.db')
    cur = conn.cursor()
    # Another SQLi vulnerability
    cur.execute(f"SELECT username, email FROM users WHERE id = {uid}")
    row = cur.fetchone()
    conn.close()

    if row:
        return f"<h3>User Info</h3><p>Username: {row[0]}<br>Email: {row[1]}</p>"
    return "User not found"

@app.route('/exec', methods=['GET', 'POST'])
def execute_command():
    if request.method == 'POST':
        cmd = request.form['cmd']
        try:
            # Remote Code Execution vulnerability
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
            return f"<pre>{output.decode()}</pre>"
        except Exception as e:
            return f"<pre>Error: {e}</pre>"

    return '''
        <form method="POST">
            Command: <input name="cmd"><br>
            <input type="submit" value="Execute">
        </form>
    '''

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
