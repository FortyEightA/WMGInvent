from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import timedelta, datetime

# create blueprint for views
views = Blueprint('views', __name__, static_folder='app/static',
                  template_folder='templates')

# path to database and images
db_path = 'WMGInvent.db'
image_path = '/app/static/assets/images'


# database table wrapper class, allows for easy interaction with the database
class Table:
    # create table if it doesn't exist
    def __init__(self, name, fields) -> None:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        self.name = name
        self.fields = ', '.join(fields)
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {name}(id INTEGER PRIMARY KEY, {self.fields})")
        cursor.close()
        conn.close()

    # get data from table with optional where clause and extra clause, fetch all or one
    def get(self, fields, where="", extra="", fetch="all"):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if fetch == "all":
            data = cursor.execute(
                f"SELECT {fields} FROM {self.name} {where} {extra}").fetchall()
        else:
            data = cursor.execute(
                f"SELECT {fields} FROM {self.name} {where} {extra}").fetchone()
        cursor.close()
        conn.close()
        return data

    # get all data from table
    def get_all(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        data = cursor.execute(f"SELECT * FROM {self.name}").fetchall()
        cursor.close()
        conn.close()
        return data

    # get data by id
    def get_by_id(self, table, id):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        data = cursor.execute(
            f"SELECT * FROM {table} WHERE id=?", (id,)).fetchone()
        cursor.close()
        conn.close()
        return data

    # execute query with values, for scenarios where query is not predefined
    def execute(self, query, values):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()

    # insert data into table
    def insert(self, columns, values):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {self.name}({columns}) VALUES({values})")
        conn.commit()
        cursor.close()
        conn.close()

    # delete data from table with where clause
    def delete(self, where):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.name} WHERE {where}")
        conn.commit()
        cursor.close()
        conn.close()

    # used for left join queries
    def left_join(self, table, on, where="", extra=""):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        data = cursor.execute(
            f"SELECT * FROM {self.name} LEFT JOIN {table} ON {on} {where} {extra}").fetchall()
        cursor.close()
        conn.close()
        return data


# create tables
users = Table('users', ['username TEXT', 'password TEXT', 'admin INTEGER'])
cars = Table('cars', ['make TEXT', 'model TEXT', 'year INTEGER',
                      'registration TEXT', 'status TEXT', 'path_to_image TEXT'])
changes = Table('changes', ['car_id INTEGER', 'change TEXT',
                            'date_start TEXT', 'date_end TEXT', 'user_id INTEGER'])


# add recent cars to session
def add_recents(id):
    if 'recents' not in session:
        session['recents'] = []
    recents = session['recents']
    if id in recents:
        session['recents'] = recents
    else:
        recents.insert(0, id)
        session['recents'] = recents


# get dates between start and end date for a car
# returns a list of dates and the change
def get_dates_between(id):
    dates = changes.get('date_start, date_end, change',
                        where=f"WHERE car_id={id}", extra="ORDER BY date_start", fetch='all')
    data = []
    for each in dates:
        temp = []
        start_date = datetime.strptime(each[0], '%Y-%m-%d')
        end_date = datetime.strptime(each[1], '%Y-%m-%d')
        while start_date <= end_date:
            temp.append(start_date.strftime('%Y-%m-%d'))
            start_date += timedelta(days=1)
        data.append([each[2], temp])
    return data


# get history of changes for all cars
def get_history():
    smallest_date = changes.get('MIN(date_start)', fetch='one')
    largets_date = changes.get('MAX(date_end)', fetch='one')
    data = []
    if smallest_date[0] is None or largets_date[0] is None:
        return data
    start_date = datetime.strptime(smallest_date[0], '%Y-%m-%d')
    end_date = datetime.strptime(largets_date[0], '%Y-%m-%d')
    while start_date <= end_date:
        date = start_date
        number_of_available = changes.get(
            'COUNT(*)', where=f"WHERE date_start<='{start_date}' AND date_end>='{start_date}' AND change='Available'", fetch='one')
        number_of_in_use = changes.get(
            'COUNT(*)', where=f"WHERE date_start<='{start_date}' AND date_end>='{start_date}' AND change='In Use'", fetch='one')
        number_of_maintenance = changes.get(
            'COUNT(*)', where=f"WHERE date_start<='{start_date}' AND date_end>='{start_date}' AND change='Maintenance'", fetch='one')
        number_of_other = changes.get(
            'COUNT(*)', where=f"WHERE date_start<='{start_date}' AND date_end>='{start_date}' AND change='Other'", fetch='one')
        data.append([date, number_of_available[0], number_of_in_use[0],
                     number_of_maintenance[0], number_of_other[0]])
        start_date += timedelta(days=1)
    return data


# get data for home page
def user_data():
    return [users.get('COUNT(*)', where="WHERE admin!=0", fetch='one')[0],
            users.get('COUNT(*)', where="WHERE admin=1", fetch='one')[0]]


# get data for home
def car_data():
    return cars.get('COUNT(*)', fetch='one')[0]


# get current status of cars
def current_status():
    dates = changes.get('date_start, date_end, change, car_id',
                        extra="ORDER BY date_start", fetch='all')
    status_count = {
        'Available': 0,
        'In Use': 0,
        'Maintenance': 0,
        'Other': 0
    }
    for each in dates:
        start_date = datetime.strptime(each[0], '%Y-%m-%d')
        end_date = datetime.strptime(each[1], '%Y-%m-%d')
        if datetime.now() >= start_date and datetime.now() <= end_date:
            # insert into dict
            if each[2] == 'Available':
                status_count['Available'] += 1
            elif each[2] == 'In Use':
                status_count['In Use'] += 1
            elif each[2] == 'Maintenance':
                status_count['Maintenance'] += 1
            else:
                status_count['Other'] += 1
    return status_count


# routes

# home route
@views.route('/')
@views.route('/home')
def home():
    if 'recents' not in session:
        session['recents'] = []
    cars_data = []
    for each in session['recents']:
        cars_data.append(cars.get_by_id('cars', each))
    current_status_data = current_status()
    full_changes_data = get_history()
    return render_template('home.html', cars_data=cars_data, status=current_status_data, changes=full_changes_data)


# fleet route
@views.route('/fleet')
def fleet():
    car_data = cars.get_all()
    return render_template('fleet.html', cars=car_data)


# car route
@views.route('/fleet/<int:id>', methods=["POST", "GET"])
def car(id):
    if request.method == "POST":
        # update car
        if request.args.get("f") == "f1":
            if request.form['make']:
                make = request.form['make']
                cars.execute(
                    "UPDATE cars SET make=? WHERE id=?", (make, id))
            if request.form['model']:
                model = request.form['model']
                cars.execute(
                    "UPDATE cars SET model=? WHERE id=?", (model, id))
            if request.form['year']:
                year = request.form['year']
                cars.execute(
                    "UPDATE cars SET year=? WHERE id=?", (year, id))
            if request.form['registration']:
                registration = request.form['registration']
                cars.execute(
                    "UPDATE cars SET registration=? WHERE id=?", (registration, id))
            else:
                registration = cars.get('registration', where=f"WHERE id={id}")

            image = request.files['image']
            # check if image is uploaded
            if request.form['make'] or request.form['model'] or request.form['year'] or request.form['registration'] or image:
                # check if image exists
                old_image = cars.get(
                    'path_to_image', where=f"WHERE id={id}", fetch='one')
                # delete old image
                old_image = old_image[0] if old_image else None
                if old_image:
                    os.remove(
                        image_path +
                        f'/{old_image}'
                    )
                    image_type = str(image.filename).split('.')[-1]
                    path_to_image = f'{registration}.{image_type}'
                    cars.execute(
                        "UPDATE cars SET path_to_image=? WHERE id=?", (path_to_image, id))
                    image.save(
                        f'{image_path}/{registration}.{str(image.filename).split(".")[-1]}')
                else:
                    image_type = str(image.filename).split('.')[-1]
                    image.save(f'{image_path}/{registration}.{image_type}')
                    path_to_image = f'{registration}.{image_type}'
            flash('Car updated successfully')
            return redirect(url_for('views.fleet'))
        # add change
        elif request.args.get("f") == "f2":
            change = request.form['change']
            date_start = request.form['date_start']
            date_end = request.form['date_end']
            user_id = users.get(
                'id', where=f"WHERE username='{session['username']}'")[0]
            if date_end < date_start:
                flash('Invalid date range')
                return redirect(url_for('views.car', id=id))
            # check if date range overlaps with existing change
            for dates in changes.get('date_start, date_end', where=f"WHERE car_id={id}", fetch='all'):
                if date_start <= dates[1] and date_end >= dates[0]:
                    flash('Date range overlaps with existing change')
                    return redirect(url_for('views.car', id=id))
                elif date_start >= dates[0] and date_end <= dates[1]:
                    flash('Date range overlaps with existing change')
                    return redirect(url_for('views.car', id=id))
                elif date_start <= dates[0] and date_end >= dates[1]:
                    flash('Date range overlaps with existing change')
                    return redirect(url_for('views.car', id=id))
                elif date_start >= dates[0] and date_end <= dates[1]:
                    flash('Date range overlaps with existing change')
                    return redirect(url_for('views.car', id=id))
                elif date_start == dates[0] and date_end == dates[1]:
                    flash('Date range overlaps with existing change')
                    return redirect(url_for('views.car', id=id))
            changes.execute(
                "INSERT INTO changes(car_id, change, date_start, date_end, user_id) VALUES(?, ?, ?, ?, ?)", (id, change, date_start, date_end, user_id[0]))
            flash('Change added successfully')
            return redirect(url_for('views.car', id=id))
        # delete car
        elif request.args.get("f") == "f3":
            cars.delete(where=f"id={id}")
            changes.delete(where=f"car_id={id}")
            flash('Car deleted successfully')
            return redirect(url_for('views.fleet'))
        # delete change
        elif request.method == "POST" and request.args.get("f") == "f4":
            change_id = request.form['change_id']
            changes.delete(where=f"id={change_id}")
            flash('Change deleted successfully')
            return redirect(url_for('views.car', id=id))
        # invalid request
        else:
            flash('Invalid request')
            return redirect(url_for('views.fleet'))
    # get car data and view car
    else:
        car = cars.get_by_id('cars', id)
        data = get_dates_between(id)
        date_data = changes.left_join(
            'users', 'changes.user_id = users.id', where=f"WHERE car_id={id}")
        add_recents(id)
        return render_template('car.html', car=car, data=data, date_data=date_data)


# search route
@views.route('/search', methods=["POST", "GET"])
def search():
    if request.method == "POST":

        if 'username' in session:
            search = request.form['search']
            print(search)
            cars_data = cars.get('id, make, model, year, registration, status, path_to_image',
                                 where=f"WHERE make LIKE '%{search}%' OR model LIKE '%{search}%' OR year LIKE '%{search}%' OR registration LIKE '%{search}%'", fetch='all')
            print(cars_data)
            flash(f'{len(cars_data)} results found')
            return render_template('fleet.html', cars=cars_data)
        else:
            return redirect(url_for('views.fleet'))
    else:
        return redirect(url_for('views.home'))


# data route
@views.route('/data')
def data():
    cars_count = car_data()
    users_data = user_data()
    full_changes_data = get_history()
    current_status_data = current_status()
    return render_template('data.html', cars_count=cars_count, users=users_data, changes=full_changes_data, status=current_status_data)


# add car route
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
        cars.execute(
            "INSERT INTO cars(make, model, year, registration, path_to_image) VALUES(?, ?, ?, ?, ?)", (make, model, year, registration, path_to_image))
        flash('Car added successfully')
        return redirect(url_for('views.fleet'))
    else:
        return render_template('add.html')


# account route
@views.route('/account')
def account():
    return render_template('account.html')


# logout route
@views.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    session.pop('admin', None)
    session.pop('recents', None)
    flash('Logged out successfully')
    return redirect(url_for('views.account'))


# register, update and delete routes
@views.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if users.get('username', where=f"WHERE username='{username}'", fetch='one'):
            flash('Username already exists')
            return render_template('register.html')
        else:
            users.execute(
                "INSERT INTO users(username, password) VALUES(?, ?)", (username, password))
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
        if users.get('username', where=f"WHERE username='{new_username}'", fetch='one'):
            users.execute("UPDATE users SET username=?, password=? WHERE username=? AND password=?",
                          (new_username, new_password, username, password))
            session['username'] = new_username
            session['password'] = new_password
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
    session.pop('admin', None)
    user_id = users.get(
        'id', where=f"WHERE username='{username}' AND password='{password}'", fetch='one')[0]
    changes.delete(f"user_id={user_id}")
    users.delete(f"username='{username}' AND password='{password}'")
    flash('User deleted successfully')
    return redirect(url_for('views.account'))


@views.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if users.get('username', where=f"WHERE username='{username}' AND password='{password}'", fetch='one'):
            session['username'] = username
            session['password'] = password
            session['admin'] = users.get(
                'admin', where=f"WHERE username='{username}'", fetch='one')[0]
            flash('Logged in successfully')
            return redirect(url_for('views.account'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    elif 'username' in session:
        flash('Already logged in')
        return redirect(url_for('views.account'))
    else:
        return render_template('login.html')
