from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
views = Blueprint('views', __name__, static_folder='app/static',
                  template_folder='templates')
db_path = '/Users/ignacyniznik/Documents/Uni/WM278/WMGInvent/WMGInvent.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
cursor.execute(
    "CREATE TABLE IF NOT EXISTS cars(id INTEGER PRIMARY KEY, make TEXT, model TEXT, year INTEGER, registration TEXT, status TEXT)"
)
cursor.execute(
    "Create table if not exists changes(id INTEGER PRIMARY KEY, car_id INTEGER, change TEXT, date TEXT)"
)
cursor.close()
conn.close()


@views.route('/')
@views.route('/home')
def home():
    return render_template('home.html')


@views.route('/account')
def account():
    return render_template('account.html')


@views.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully')
    return redirect(url_for('views.account'))


@views.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
            flash('Username already exists')
            return render_template('register.html')
        else:
            cursor.execute(
                "INSERT INTO users(username, password) VALUES(?, ?)", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('User registered successfully')
            return redirect(url_for('views.login'))
    else:
        return render_template('register.html')


@views.route('/update', methods=["POST", "GET"])
def update():
    if request.method == "POST":
        username = session['username']
        password = session['password']
        session.pop('username', None)
        session.pop('password', None)
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone():
            cursor.execute("UPDATE users SET username=?, password=? WHERE username=? AND password=?",
                           (new_username, new_password, username, password))
            session['username'] = new_username
            session['password'] = new_password
            conn.commit()
            cursor.close()
            conn.close()
            flash('User updated successfully')
            return redirect(url_for('views.account'))
        else:
            flash('Invalid username or password')
            return render_template('update.html')
    else:
        return render_template('update.html')


@views.route('/delete')
def delete():
    username = session['username']
    password = session['password']
    session.pop('username', None)
    session.pop('password', None)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, password)).fetchone()
    cursor.execute(
        "DELETE FROM users WHERE username=? AND password=?", (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User deleted successfully')
    return redirect(url_for('views.account'))


@views.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone():
            session['username'] = username
            session['password'] = password
            cursor.close()
            conn.close()
            flash('Logged in successfully')
            return redirect(url_for('views.account'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    else:
        return render_template('login.html')
