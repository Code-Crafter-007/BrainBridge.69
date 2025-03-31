from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib  # Added for password hashingflask

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your secret key'

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'surajmeena1234'  # Change this for security
app.config['MYSQL_DB'] = 'brainbridgelogin'

mysql = MySQL(app)

# ----------------- LOGIN ROUTE -----------------
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash password before checking

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND user_password = %s', (username, hashed_password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username or password!'
    return render_template('login.html', msg=msg)


@app.route("/dashboard")
def dashboard():
    if "user" in session:  # Check if user is logged in
        return render_template("dashboard.html")  # Render BrainBridge page
    return redirect(url_for("login"))  # If not logged in, redirect to login

@app.route('/profile')
def profile():
        return render_template("profile.html")
# ----------------- LOGOUT ROUTE -----------------
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.clear(0)
    return redirect(url_for('login'))


# ----------------- REGISTER ROUTE -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Hash password before storing

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts (username, user_password, email) VALUES (%s, %s, %s)', (username, hashed_password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('register.html', msg=msg)

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/connect')
def connect():
    return render_template("connect.html")

@app.route('/notes')
def notes():
    return render_template('notes.html')


if __name__ == "__main__":
    app.run(debug=True)