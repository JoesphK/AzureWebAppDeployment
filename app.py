from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc

def get_db_connection():
    conn = pyodbc.connect(app.config['AZURE_SQL_CONNECTION_STRING'])
    return conn
import re

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['AZURE_SQL_CONNECTION_STRING'] = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={app.config['MYSQL_HOST']},{app.config['PORT']};"
    f"DATABASE={app.config['MYSQL_DB']};"
    f"UID={app.config['MYSQL_USER']};"
    f"PWD={app.config['MYSQL_PASSWORD']};"
    "ENCRYPT=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0] # Assuming id is the first column
            session['username'] = account[1] # Assuming username is the second column
            msg = 'Logged in successfully!'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)', (username, password, email,))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM accounts WHERE id = ?', (session['id'],))
        account = cursor.fetchone()
        if account:
            account_dict = {
                'id': account[0],
                'username': account[1],
                'email': account[2]
            }
            return render_template('profile.html', account=account_dict)
    return redirect(url_for('login'))

@app.route('/users')
def users():
    if 'loggedin' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email FROM accounts')
        users_data = cursor.fetchall()
        users = []
        for user in users_data:
            users.append({
                'id': user[0],
                'username': user[1],
                'email': user[2]
            })
        return render_template('users.html', users=users)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)