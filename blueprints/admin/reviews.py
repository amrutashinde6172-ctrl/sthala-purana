from . import admin_bp
from flask import render_template, redirect, url_for
from models import Review, db

@admin_bp.route('/reviews')
def reviews():
    data = Review.query.all()
    return render_template("admin/reviews.html", data=data)


@admin_bp.route('/reviews/<action>/<int:id>')
def review_action(action, id):

    review = Review.query.get_or_404(id)

    if action == "approve":
        review.status = "approved"

    elif action == "hide":
        review.status = "hidden"

    elif action == "delete":
        db.session.delete(review)

    db.session.commit()
    return redirect(url_for('admin.reviews'))