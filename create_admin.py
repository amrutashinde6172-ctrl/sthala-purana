from app import app
from models import db, User

with app.app_context():
    admin = User(
        username="amruta",
        email="amrutashinde6172@gmail.com",
        role="admin",
        is_admin=True
    )

    admin.set_password("#amruta2003")

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully")