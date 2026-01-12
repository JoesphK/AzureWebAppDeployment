from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
import re

app = Flask(__name__)
app.secret_key = 'your secret key'

# Azure SQL Database connection
def get_db_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=serverazsqldb.database.windows.net;'
        'DATABASE=AZSQLDB;'
        'UID=Youssef@serverazsqldb;'
        'PWD=GBG_Academy!;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
    )

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, username FROM accounts WHERE username = ? AND password = ?',
            (username, password)
        )
        account = cursor.fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Username must contain only letters and numbers!'
        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT id FROM accounts WHERE username = ?',
                (username,)
            )
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute(
                    'INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)',
                    (username, password, email)
                )
                conn.commit()
                msg = 'You have successfully registered!'

            conn.close()

    return render_template('register.html', msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return "DB connection OK"
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
