from . import admin_bp
from flask import render_template, redirect, url_for
from models import User, db


@admin_bp.route('/users')
def users():
    data = User.query.all()
    return render_template("admin/users.html", data=data)


@admin_bp.route('/users/<action>/<int:id>')
def user_action(action, id):

    user = User.query.get_or_404(id)

    if action == "activate":
        user.status = "active"

    elif action == "deactivate":
        user.status = "inactive"

    elif action == "promote":
        user.role = "admin"

    db.session.commit()
    return redirect(url_for('admin.users'))
