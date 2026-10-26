from . import admin_bp
from flask import render_template
from models import User, Temple, Accommodation, TravelAgent, TravelPackage

@admin_bp.route('/dashboard')
def dashboard():

    return render_template("admin/dashboard.html",
        users=User.query.count(),
        temples=Temple.query.count(),
        properties=Accommodation.query.count(),
        agents=TravelAgent.query.count(),
        packages=TravelPackage.query.count()
    )