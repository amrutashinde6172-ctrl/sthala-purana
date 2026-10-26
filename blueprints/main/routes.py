from . import main_bp

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from models import (
    db,
    Accommodation,
    TravelPackage,
    TravelAgent
)


# ---------------- BECOME AGENT ----------------
@main_bp.route('/become-agent', methods=['GET', 'POST'])
def become_agent():

    if request.method == 'POST':

        agent = TravelAgent(
            name=request.form.get('name'),
            company=request.form.get('company'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            specialization=request.form.get('specialization'),
            status='pending'
        )

        db.session.add(agent)
        db.session.commit()

        flash(
            "Application submitted successfully. Waiting for admin approval.",
            "success"
        )

        return redirect(url_for('travel_agents'))

    return render_template('become_agent.html')


# ---------------- HOME ----------------
@main_bp.route('/')
def home():
    return render_template('index.html')


# ---------------- ABOUT ----------------
@main_bp.route('/about')
def about():
    return render_template('about.html')


# ---------------- CONTACT ----------------
@main_bp.route('/contact')
def contact():
    return render_template('contact.html')


# ---------------- ACCOMMODATIONS ----------------
@main_bp.route('/accommodations')
def accommodations():

    data = Accommodation.query.filter_by(
        status="approved"
    ).all()

    return render_template(
        'accommodations.html',
        data=data
    )


# ---------------- TRAVEL PACKAGES ----------------
@main_bp.route('/packages')
def packages():

    data = TravelPackage.query.filter_by(
        status="approved"
    ).all()

    return render_template(
        'packages.html',
        data=data
    )