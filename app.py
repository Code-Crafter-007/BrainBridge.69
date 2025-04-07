from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import date, timedelta


from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib  # Added for password hashingflask

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your secret key'

# Database configurationCCCc
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'surajmeena1234'  # Change this for security
app.config['MYSQL_DB'] = 'brainbridgelogin'

mysql = MySQL(app)
#-------------------Flask login configure------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


#--------------User class-----------------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (user_id,))
    account = cursor.fetchone()
    if account:
        return User(account['id'], account['username'])
    return None


# ----------------- LOGIN ROUTE -----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        input_value = request.form['username']  # can be username or email
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if input_value is an email or username
        if '@' in input_value:
            cursor.execute('SELECT * FROM accounts WHERE email = %s AND user_password = %s', (input_value, hashed_password))
        else:
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND user_password = %s', (input_value, hashed_password))

        account = cursor.fetchone()

        if account:
            user = User(id=account['id'], username=account['username'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username/email or password!'
    return render_template('login.html', msg=msg)




@app.route('/profile')
@login_required
def profile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT streak, badge_earned, branch, year FROM accounts WHERE id = %s', (current_user.id,))
    account = cursor.fetchone()

    progress_data = {
        "Mon": 2,
        "Tue": 1,
        "Wed": 3,
        "Thu": 2,
        "Fri": 2.5,
        "Sat": 1.5,
        "Sun": 3
    }

    return render_template(
        'profile.html',
        username=current_user.username,
        progress_data=progress_data,
        streak=account['streak'],
        badge_earned=account['badge_earned'],
        branch=account['branch'],
        year=account['year']
    )




# ----------------- LOGOUT ROUTE -----------------
@app.route('/logout')
def logout():
    logout_user()
    session.clear() 
    return redirect(url_for('login'))



# ----------------- REGISTER ROUTE -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        branch = request.form['branch']
        year = request.form['year']
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
        elif not username or not password or not email or not branch or not year:
            msg = 'Please fill out the form completely!'
        else:
            cursor.execute('INSERT INTO accounts (username, user_password, email, branch, year) VALUES (%s, %s, %s, %s, %s)', 
                           (username, hashed_password, email, branch, year))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form completely!'
    
    return render_template('register.html', msg=msg)


@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/index')
def index():
    return render_template("index.html")
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


@app.route('/connect')
def connect():
    return render_template("connect.html")


@app.route('/syllabus')
def syllabus():
    return render_template("syllabus.html")

@app.route('/notes')
def notes():
    return render_template('notes.html')


if __name__ == "__main__":
    app.run(debug=True)