from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
views = Blueprint('views', __name__, static_folder='app/static',
                  template_folder='templates')
db_path = '/Users/ignacyniznik/Documents/Uni/WM278/WMGInvent/WMGInvent.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
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
            return redirect(url_for('views.login'))
    else:
        return render_template('register.html')


@views.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone():
            cursor.close()
            conn.close()
            return redirect(url_for('views.account'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    else:
        return render_template('login.html')
