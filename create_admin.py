from Website import create_app, db
from Website.models import User
from werkzeug.security import generate_password_hash

# Create the app and push context
app = create_app()
app.app_context().push()

# Check if admin already exists
admin_email = "admin@admin.com"
existing_admin = User.query.filter_by(email=admin_email).first()

if existing_admin:
    print(f"Admin with email '{admin_email}' already exists.")
else:
    # Create the admin user
    admin_user = User(
        email=admin_email,
        password=generate_password_hash("academicwizard"),
        first_name="Admin",
        last_name="User",
        role="admin"
    )
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin account created successfully! Email: {admin_email}, Password: academicwizard")
