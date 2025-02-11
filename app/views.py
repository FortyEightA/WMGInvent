from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
views = Blueprint('views', __name__, static_folder='app/static',
                  template_folder='templates')
db_path = '/Users/ignacyniznik/Documents/Uni/WM278/WMGInvent/WMGInvent.db'
image_path = '/Users/ignacyniznik/Documents/Uni/WM278/WMGInvent/app/static/assets/images'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, admin INTEGER)")
cursor.execute(
    "CREATE TABLE IF NOT EXISTS cars(id INTEGER PRIMARY KEY, make TEXT, model TEXT, year INTEGER, registration TEXT, status TEXT, path_to_image TEXT)"
)
cursor.execute(
    "Create table if not exists changes(id INTEGER PRIMARY KEY, car_id INTEGER, change TEXT, date TEXT, user_id INTEGER)")
cursor.close()
conn.close()


@views.route('/')
@views.route('/home')
def home():
    return render_template('home.html')


@views.route('/fleet')
def fleet():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cars = cursor.execute("SELECT * FROM cars").fetchall()
    cursor.close()
    conn.close()
    print(cars)
    return render_template('fleet.html', cars=cars)


@views.route('/fleet/<int:id>', methods=["POST", "GET"])
def car(id):
    if request.method == "POST":
        if request.args.get("f") == "f1":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            if request.form['make']:
                make = request.form['make']
                cursor.execute("UPDATE cars SET make=? WHERE id=?", (make, id))
            if request.form['model']:
                model = request.form['model']
                cursor.execute(
                    "UPDATE cars SET model=? WHERE id=?", (model, id))
            if request.form['year']:
                year = request.form['year']
                cursor.execute("UPDATE cars SET year=? WHERE id=?", (year, id))
            if request.form['registration']:
                registration = request.form['registration']
                cursor.execute(
                    "UPDATE cars SET registration=? WHERE id=?", (registration, id))
            else:
                registration = cursor.execute(
                    "SELECT registration FROM cars WHERE id=?", (id,)).fetchone()[0]

            image = request.files['image']
            if request.form['make'] or request.form['model'] or request.form['year'] or request.form['registration']:
                old_image = cursor.execute(
                    "SELECT path_to_image FROM cars WHERE id=?", (id,)).fetchone()
                if old_image:
                    os.rename(
                        f'{image_path}/{old_image[0]}', f'{image_path}/{registration}.{str(image.filename).split(".")[-1]}')
                    path_to_image = f'{registration}.{str(image.filename).split(".")[-1]}'
                    cursor.execute(
                        "UPDATE cars SET path_to_image=? WHERE id=?", (path_to_image, id))
                else:
                    image_type = str(image.filename).split('.')[-1]
                    image.save(f'{image_path}/{registration}.{image_type}')
                    path_to_image = f'{registration}.{image_type}'
            conn.commit()
            cursor.close()
            conn.close()
            flash('Car updated successfully')
            return redirect(url_for('views.fleet'))
        elif request.args.get("f") == "f2":
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            change = request.form['change']
            date = request.form['date']
            user_id = cursor.execute(
                "SELECT id FROM users WHERE username=?", (session['username'],)).fetchone()[0]
            cursor.execute(
                "INSERT INTO changes(car_id, change, date, user_id) VALUES(?, ?, ?, ?)", (id, change, date, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Change added successfully')
            return redirect(url_for('views.car', id=id))
        else:
            flash('Invalid request')
            return redirect(url_for('views.fleet'))
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        car = cursor.execute("SELECT * FROM cars WHERE id=?", (id,)).fetchone()
        cursor.close()
        conn.close()
        return render_template('car.html', car=car)


@views.route('/fleet/add', methods=["POST", "GET"])
def add_car():
    if request.method == "POST":
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        registration = request.form['registration']
        image = request.files['image']
        if image:
            image_type = str(image.filename).split('.')[-1]
            image.save(f'{image_path}/{registration}.{image_type}')
            path_to_image = f'{registration}.{image_type}'
        else:
            path_to_image = None
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cars(make, model, year, registration, path_to_image) VALUES(?, ?, ?, ?, ?)", (make, model, year, registration, path_to_image))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Car added successfully')
        return redirect(url_for('views.fleet'))
    else:
        return render_template('add.html')


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
