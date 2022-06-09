import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db_cursor, get_db_connection


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fullname = request.form['fullname']
        role = request.form['user_role']

        conn = get_db_connection()
        cur = get_db_cursor(conn)
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not role:
            error = 'Please select the role'
        elif not fullname:
            error = 'Full Name is required'

        if error is None:
        # try:
            cur.execute(
                f"INSERT INTO {role} (username, password, fullname, email)" +\
                " VALUES (%s, %s, %s, %s)",
                (username, generate_password_hash(password), fullname, email),
            )
            conn.commit()
        # except Exception:
        #     error = f"Something went wrong"
        #     print("jopa")
        #     conn.rollback()
        # else:
            cur.close()
            return redirect(url_for("auth.login"))

        cur.close()
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['user_role']

        cur = get_db_cursor()

        error = None
        cur.execute(
            f'SELECT * FROM {role} WHERE username = %s', (username,)
        )
        user = cur.fetchone()
        cur.close()  # maybe need to move the line right at the end

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_fullname'] = user['fullname']
            session['user_role'] = role
            return redirect(url_for('hello'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    role = session.get('user_role')

    if user_id is None:
        g.user = None
    else:
        cur = get_db_cursor()

        cur.execute(
            f'SELECT * FROM {role} WHERE id = %s', (user_id,)
        )
        g.user = cur.fetchone()

        cur.close()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
