from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app, jsonify
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Bookings, Resources, Contact
from flask_login import login_user, login_required, logout_user, current_user
from .decorators import role_required
import os
from datetime import datetime, timedelta



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

@views.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        reason = request.form.get('reason')

        if not email or not reason:
            flash("All fields are required", "error")
        else:
            contact_msg = Contact(email=email, reason=reason)
            db.session.add(contact_msg)
            db.session.commit()
            flash("Message sent!", "success")
            return redirect(url_for('views.contact'))

    return render_template('contact.html')


@views.route('/admin/contacts', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def contacts():  
    contacts = Contact.query.all()
    return render_template('admin/contacts.html', contacts=contacts)

@views.route('/api/bookings')
@login_required
def bookings_api():
    # If query parameter tutor_id is provided, filter by it
    tutor_id = request.args.get('tutor_id', type=int)

    # If the current user is a tutor and no tutor_id is provided, show only their bookings
    if current_user.role == 'tutor' and not tutor_id:
        bookings = Bookings.query.filter_by(tutor_id=current_user.user_id).all()
    elif tutor_id:
        bookings = Bookings.query.filter_by(tutor_id=tutor_id).all()
    else:
        bookings = Bookings.query.all()  # admin sees all bookings

    events = []
    for b in bookings:
        events.append({
            "title": f"{b.student.first_name} {b.student.last_name}",
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
        })

    return jsonify(events)



@views.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        data = request.get_json()

        tutor_id = int(data['tutor_id'])
        subject = data.get('subject')
        start = datetime.fromisoformat(data['start'])
        duration_minutes = int(data.get('duration', 30))  
        end = start + timedelta(minutes=duration_minutes)

        if not subject:
            return jsonify({"error": "Subject is required"}), 400

        # Prevent double booking for the tutor
        conflict = Bookings.query.filter(
            Bookings.tutor_id == tutor_id,
            Bookings.start_time < end,
            Bookings.end_time > start
        ).first()

        if conflict:
            return jsonify({"error": "This tutor is already booked for that time"}), 400

        booking = Bookings(
            tutor_id=tutor_id,
            student_id=current_user.user_id,
            start_time=start,
            end_time=end
        )

        db.session.add(booking)
        db.session.commit()

        return jsonify({"success": True})

    # GET request: render template with list of tutors
    tutors = User.query.filter_by(role='tutor').all()
    return render_template('booking.html', tutors=tutors)



@views.route('/tutor/home')
@login_required
@role_required('tutor')
def tutor_bookings():
    # Tutors only see their bookings
    return render_template('tutor/home.html')



