from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "academic_wizard.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'PETR2140'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = 'website/static/resources'

    db.init_app(app)

    # Import blueprints here
    from .root import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Import models here to avoid circular import
    from .models import User, Bookings, Resources
    with app.app_context():
        db.create_all()

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
