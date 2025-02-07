from flask import Blueprint, render_template, request, redirect, url_for, session

views = Blueprint('views', __name__, static_folder='static',
                  template_folder='templates')


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


@views.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('views.account'))
    else:
        return render_template('login.html')
