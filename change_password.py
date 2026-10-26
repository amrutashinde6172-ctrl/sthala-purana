from app import app
from models import db, User

with app.app_context():
    admin = User.query.filter_by(email="amrutashinde6172@gmail.com").first()

    if admin:
        admin.set_password("#amruta123")
        db.session.commit()
        print("Password updated successfully")
    else:
        print("Admin not found")
