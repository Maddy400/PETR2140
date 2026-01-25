from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Bookings, Resources
from flask_login import login_user, login_required, logout_user, current_user
from .decorators import role_required
import os



views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user = current_user)

@views.route('/admin')
@login_required
@role_required('admin')
def admin_home():
    return render_template('admin/dashboard.html')


@views.route('/tutor')
@login_required
@role_required('tutor', 'admin')
def tutor_home():
    return render_template('tutor/home.html')


@views.route('/admin/tutors')
@login_required
@role_required('admin')
def manage_tutors():
    tutors = User.query.filter_by(role='tutor').all()
    return render_template('admin/tutors.html', tutors=tutors)


@views.route('/admin/tutors/add', methods=['POST'])
@login_required
@role_required('admin')
def add_tutor():
    email = request.form.get('email')

    if User.query.filter_by(email=email).first():
        flash("Tutor already exists", "error")
        return redirect(url_for('views.manage_tutors'))

    tutor = User(
        email=email,
        first_name=request.form.get('first_name'),
        last_name=request.form.get('last_name'),
        password=generate_password_hash(request.form.get('password')),
        role='tutor'
    )

    db.session.add(tutor)
    db.session.commit()
    flash("Tutor added", "success")

    return redirect(url_for('views.manage_tutors'))


@views.route('/admin/tutors/delete/<int:user_id>')
@login_required
@role_required('admin')
def delete_tutor(user_id):
    tutor = User.query.get_or_404(user_id)

    if tutor.role != 'tutor':
        abort(403)

    db.session.delete(tutor)
    db.session.commit()
    flash("Tutor deleted", "success")

    return redirect(url_for('views.manage_tutors'))

@views.route('/admin/tutors/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_tutor(user_id):
    tutor = User.query.get_or_404(user_id)

    if tutor.role != 'tutor':
        abort(403)

    if request.method == 'POST':
        tutor.email = request.form.get('email')
        tutor.first_name = request.form.get('first_name')
        tutor.last_name = request.form.get('last_name')

        db.session.commit()
        flash("Tutor updated", "success")
        return redirect(url_for('views.manage_tutors'))

    return render_template('admin/edit_tutor.html', tutor=tutor)


from .models import Bookings

@views.route('/admin/bookings')
@login_required
@role_required('admin')
def manage_bookings():
    bookings = Bookings.query.all()
    return render_template('admin/bookings.html', bookings=bookings)


@views.route('/admin/bookings/cancel/<int:booking_id>')
@login_required
@role_required('admin')
def cancel_booking(booking_id):
    booking = Bookings.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking cancelled", "success")

    return redirect(url_for('views.manage_bookings'))

@views.route('/admin/resources', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def manage_resources():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))

        resource = Resources(title=file.filename, filename=file.filename)
        db.session.add(resource)
        db.session.commit()

        flash("Resource uploaded", "success")

    resources = Resources.query.all()
    return render_template('admin/resources.html', resources=resources)

@views.route('/admin/stats')
@login_required
@role_required('admin')
def site_stats():
    return render_template(
        'admin/stats.html',
        users=User.query.count(),
        tutors=User.query.filter_by(role='tutor').count(),
        bookings=Bookings.query.count()
    )
