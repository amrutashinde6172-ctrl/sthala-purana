from app import app, db, User

with app.app_context():
    admin = User.query.filter_by(email="sthalapurana27@gmail.com").first()

    if admin:
        admin.username = "NEW_ADMIN"
        admin.email = "amrutashnde6172@gmail.com"
        admin.is_admin = True
        admin.set_password("#amruta123")

        db.session.commit()
        print("Admin updated successfully")
    else:
        print("Admin not found")