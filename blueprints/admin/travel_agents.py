from . import admin_bp
from flask import render_template, redirect, url_for
from models import TravelAgent, db
from flask import render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import os
@main_bp.route('/become-agent', methods=['GET', 'POST'])
def become_agent():

     if request.method == 'POST':

        image = request.files.get('image')

        filename = None

        if image and image.filename:
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    'static/uploads/agents',
                    filename
                )
            )

        agent = TravelAgent(
            agency_name=request.form.get('agency_name'),
            contact_person=request.form.get('contact_person'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            city=request.form.get('city'),
            status='pending'
        )

        db.session.add(agent)
        db.session.commit()

        flash('Application submitted successfully')
        return redirect('/')

    return render_template('become_agent.html')
@admin_bp.route('/travel-agents')
def travel_agents():
    data = TravelAgent.query.all()
    return render_template("admin/travel_agents.html", data=data)


@admin_bp.route('/travel-agents/<action>/<int:id>')
def agent_action(action, id):

    agent = TravelAgent.query.get_or_404(id)

    if action == "approve":
        agent.status = "approved"

    elif action == "reject":
        agent.status = "rejected"

    elif action == "suspend":
        agent.status = "suspended"

    db.session.commit()
    return redirect(url_for('admin.travel_agents'))