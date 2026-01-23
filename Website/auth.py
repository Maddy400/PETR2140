from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged In Successfully', category = 'success')
                
                if user.role == 'admin':
                    return redirect(url_for('views.admin_home'))

                elif user.role == 'tutor':
                    return redirect(url_for('views.tutor_home'))
                
                else:
                    return redirect(url_for('views.home'))
            else:
                flash("Incorrect password", category = 'error')
        else:
            flash("Email does not exist", category = 'error')

    return render_template("login.html", user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category = 'error')

        if len(email) < 4:
            flash("Email must be greater than 3 characters", category = 'error')
        elif len(first_name) < 2:
            flash("First name should be longer than 1 character", category = 'error')
        elif len(last_name) < 2:
            flash("Last name should be longer than 1 character", category = 'error')
        elif password1 != password2:
            flash("Passwords do not match", category = 'error')
        elif len(password1) < 8:
            flash("Password should be longer than 8 characters", category = 'error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1), role='student')

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("Account Created", category = 'success')
            return redirect(url_for('views.home'))


    return render_template("sign_up.html", user = current_user)
