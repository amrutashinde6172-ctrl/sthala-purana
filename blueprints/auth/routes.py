from . import auth_bp
from flask import render_template, request, redirect, url_for, session, flash

from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------- REGISTER ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ---------------- LOGIN ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):

            session['user_id'] = user.id
            session['role'] = user.role

            return redirect(url_for('main.home'))

        flash("Invalid email or password")

    return render_template('auth/login.html')


# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))