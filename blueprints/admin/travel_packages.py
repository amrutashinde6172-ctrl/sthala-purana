from . import admin_bp
from flask import render_template, redirect, url_for
from models import TravelPackage, db

@admin_bp.route('/travel-packages')
def travel_packages():
    data = TravelPackage.query.all()
    return render_template("admin/travel_packages.html", data=data)


@admin_bp.route('/travel-packages/<action>/<int:id>')
def package_action(action, id):

    pkg = TravelPackage.query.get_or_404(id)

    if action == "approve":
        pkg.status = "approved"

    elif action == "reject":
        pkg.status = "rejected"

    elif action == "suspend":
        pkg.status = "suspended"

    db.session.commit()
    return redirect(url_for('admin.travel_packages'))