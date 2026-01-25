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


    bookings_as_student = db.relationship('Bookings', backref='student', foreign_keys='Bookings.user_id')
    bookings_as_tutor = db.relationship('Bookings', backref='tutor', foreign_keys='Bookings.tutor_id')

    def get_id(self):
        return str(self.user_id)

class Bookings(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    date = db.Column(db.DateTime)
    time = db.Column(db.DateTime)

class Resources(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(150), nullable=False)

class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.String(10000), nullable=False)