from . import admin_bp
from flask import render_template, redirect, url_for
from models import Temple, db

@admin_bp.route('/temples')
def temples():
    data = Temple.query.all()
    return render_template("admin/temples.html", data=data)


@admin_bp.route('/temples/<action>/<int:id>')
def temple_action(action, id):

    item = Temple.query.get_or_404(id)

    if action == "delete":
        db.session.delete(item)

    db.session.commit()
    return redirect(url_for('admin.temples'))