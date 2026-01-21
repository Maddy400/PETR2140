from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    booking = db.relationship('Bookings')

class Tutor(db.Model, UserMixin):
    tutor_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    booking = db.relationship('Bookings')

class Admin(db.Model, UserMixin):
    admin_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))

class Bookings(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.tutor_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    date = db.Column(db.DateTime)
    time = db.Column(db.DateTime)


class Resources(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    resource_url = db.Column(db.String)