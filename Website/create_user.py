from Website import create_app, db
from Website.models import User
from werkzeug.security import generate_password_hash

# Initialize Flask app context
app = create_app()
app.app_context().push()

# Check if admin already exists
if User.query.filter_by(email="admin@admin.com").first():
    print("Admin already exists!")
else:
    admin = User(
        email="admin@admin.com",
        first_name="Admin",
        last_name="User",
        password=generate_password_hash("academicwizard"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!")
