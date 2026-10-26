from . import admin_bp
from flask import render_template, redirect, url_for
from models import Contact, db

@admin_bp.route('/contacts')
def contacts():
    data = Contact.query.all()
    return render_template("admin/contacts.html", data=data)


@admin_bp.route('/contacts/<action>/<int:id>')
def contact_action(action, id):

    msg = Contact.query.get_or_404(id)

    if action == "read":
        msg.status = "read"

    elif action == "delete":
        db.session.delete(msg)

    db.session.commit()
    return redirect(url_for('admin.contacts'))