from . import admin_bp
from flask import render_template, redirect, url_for
from models import Accommodation, db

@admin_bp.route('/accommodations')
def accommodations():
    data = Accommodation.query.all()
    return render_template("admin/accommodations.html", data=data)


@admin_bp.route('/accommodations/<action>/<int:id>')
def accommodation_action(action, id):

    item = Accommodation.query.get_or_404(id)

    if action == "approve":
        item.status = "approved"

    elif action == "reject":
        item.status = "rejected"

    elif action == "suspend":
        item.status = "suspended"

    db.session.commit()
    return redirect(url_for('admin.accommodations'))