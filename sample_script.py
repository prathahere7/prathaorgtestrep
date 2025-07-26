from flask import Flask, request, render_template_string, redirect, url_for
import subprocess
import os

app = Flask(__name__)

users = {}

# Home route
@app.route('/')
def index():
    return '''
        <h1>Welcome to the XSS + RCE Lab</h1>
        <ul>
            <li><a href="/register">Register</a></li>
            <li><a href="/login">Login</a></li>
            <li><a href="/comment">Leave a Comment (XSS)</a></li>
            <li><a href="/admin">Admin Tools (RCE)</a></li>
        </ul>
    '''

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form.get('username')
        passwd = request.form.get('password')
        if uname in users:
            return "User already exists!"
        users[uname] = passwd
        return redirect('/login')
    
    return '''
        <h2>Register</h2>
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password"><br>
            <input type="submit" value="Register">
        </form>
    '''

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('username')
        passwd = request.form.get('password')
        if users.get(uname) == passwd:
            return f"<h3>Welcome, {uname}!</h3><a href='/'>Go back</a>"
        return "Invalid login"
    
    return '''
        <h2>Login</h2>
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# Store comments in memory (not safe)
comments = []

# XSS-vulnerable comment section
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        username = request.form.get('username')
        content = request.form.get('comment')
        # 🚨 No sanitization — vulnerable to XSS
        comments.append({'user': username, 'text': content})
        return redirect('/comment')
    
    comment_html = ''
    for c in comments:
        comment_html += f"<p><strong>{c['user']}:</strong> {c['text']}</p>\n"
    
    return f'''
        <h2>Public Comment Wall</h2>
        <form method="POST">
            Name: <input name="username"><br>
            Comment: <input name="comment"><br>
            <input type="submit" value="Post Comment">
        </form>
        <hr>
        <div>{comment_html}</div>
        <a href="/">Back</a>
    '''

# Admin RCE tool
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        cmd = request.form.get('command')
        try:
            # 🚨 Vulnerable to RCE
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
            result = output.decode()
        except Exception as e:
            result = f"Error: {e}"
        
        return f'''
            <h2>Admin Command Execution</h2>
            <form method="POST">
                Command: <input name="command" style="width:300px;"><br>
                <input type="submit" value="Execute">
            </form>
            <h3>Output:</h3>
            <pre>{result}</pre>
            <a href="/">Back</a>
        '''
    
    return '''
        <h2>Admin Command Execution</h2>
        <form method="POST">
            Command: <input name="command" style="width:300px;"><br>
            <input type="submit" value="Execute">
        </form>
        <a href="/">Back</a>
    '''

# Fake admin login (for completeness)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('adminuser')
        pw = request.form.get('adminpass')
        if user == 'admin' and pw == 'admin123':
            return redirect('/admin')
        return "Access denied"
    
    return '''
        <h2>Admin Login</h2>
        <form method="POST">
            Admin Username: <input name="adminuser"><br>
            Admin Password: <input name="adminpass"><br>
            <input type="submit" value="Login">
        </form>
    '''

# View environment variables (more fun RCE)
@app.route('/env')
def env_vars():
    # 🚨 RCE-like exposure
    envs = "<br>".join([f"{k} = {v}" for k, v in os.environ.items()])
    return f"<h3>Server Environment Variables</h3><pre>{envs}</pre><a href='/'>Back</a>"

# Start the app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
