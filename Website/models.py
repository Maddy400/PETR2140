from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(15), nullable=False, default='student')

    bookings_as_student = db.relationship(
        'Bookings',
        foreign_keys='Bookings.student_id',
        backref='student'
    )

    bookings_as_tutor = db.relationship(
        'Bookings',
        foreign_keys='Bookings.tutor_id',
        backref='tutor'
    )

    def get_id(self):
        return str(self.user_id)


class Bookings(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)

    tutor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(db.DateTime, server_default=func.now())

    subject = db.Column(db.String, nullable=False)


class Resources(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(150), nullable=False)


class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(10000), nullable=False)
