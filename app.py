from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import json
import os
import secrets
from blueprints.main import main_bp

from models import (
    db,
    User,
    Temple,
    Review,
    Favorite,
    TripPlan,
    Accommodation,
    TravelPackage,
    TravelAgent,
    ContactMessage,
    Announcement
)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sthala_purana.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Register blueprints AFTER app creation
app.register_blueprint(main_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────
def update_temple_rating(temple_id):
    temple = Temple.query.get(temple_id)
    reviews = Review.query.filter_by(temple_id=temple_id, is_approved=True).all()
    if reviews:
        temple.rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
        temple.review_count = len(reviews)
    else:
        temple.rating = 0.0
        temple.review_count = 0
    db.session.commit()


# ─────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    featured_temples = Temple.query.filter_by(is_featured=True, is_active=True).limit(6).all()
    top_rated = Temple.query.filter_by(is_active=True).order_by(Temple.rating.desc()).limit(4).all()
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(3).all()
    total_temples = Temple.query.filter_by(is_active=True).count()
    states = db.session.query(Temple.state).distinct().count()
    total_users = User.query.filter_by(is_active=True).count()
    return render_template('index.html',
                           featured_temples=featured_temples,
                           top_rated=top_rated,
                           announcements=announcements,
                           total_temples=total_temples,
                           states=states,
                           total_users=total_users)


@app.route('/temples')
def temples():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    state_filter = request.args.get('state', '')
    deity_filter = request.args.get('deity', '')
    type_filter = request.args.get('type', '')
    sort_by = request.args.get('sort', 'name')

    query = Temple.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            Temple.name.ilike(f'%{search}%') |
            Temple.deity.ilike(f'%{search}%') |
            Temple.city.ilike(f'%{search}%') |
            Temple.state.ilike(f'%{search}%')
        )

    if state_filter:
        query = query.filter(Temple.state == state_filter)

    if deity_filter:
        query = query.filter(Temple.deity.ilike(f'%{deity_filter}%'))

    if type_filter:
        query = query.filter(Temple.temple_type == type_filter)

    if sort_by == 'rating':
        query = query.order_by(Temple.rating.desc())
    elif sort_by == 'newest':
        query = query.order_by(Temple.created_at.desc())
    else:
        query = query.order_by(Temple.name)

    temples_paginated = query.paginate(page=page, per_page=12, error_out=False)

    states = db.session.query(Temple.state).distinct().order_by(Temple.state).all()
    deities = db.session.query(Temple.deity).distinct().order_by(Temple.deity).all()
    types = db.session.query(Temple.temple_type).distinct().order_by(Temple.temple_type).all()

    return render_template(
        'temples.html',
        temples=temples_paginated,
        states=[s[0] for s in states if s[0]],
        deities=[d[0] for d in deities if d[0]],
        types=[t[0] for t in types if t[0]],
        search=search,
        state_filter=state_filter,
        deity_filter=deity_filter,
        type_filter=type_filter,
        sort_by=sort_by
    )


@app.route('/temple/<int:temple_id>')
def temple_detail(temple_id):
    temple = Temple.query.get_or_404(temple_id)
    reviews = Review.query.filter_by(temple_id=temple_id, is_approved=True).order_by(Review.created_at.desc()).all()
    gallery = json.loads(temple.gallery_images) if temple.gallery_images else []
    user_review = None
    is_favorite = False
    if current_user.is_authenticated:
        user_review = Review.query.filter_by(temple_id=temple_id, user_id=current_user.id).first()
        is_favorite = Favorite.query.filter_by(user_id=current_user.id, temple_id=temple_id).first() is not None
    similar = Temple.query.filter(
        Temple.state == temple.state,
        Temple.id != temple.id,
        Temple.is_active == True
    ).limit(4).all()
    return render_template('temple_detail.html',
                           temple=temple,
                           reviews=reviews,
                           gallery=gallery,
                           user_review=user_review,
                           is_favorite=is_favorite,
                           similar_temples=similar)


@app.route('/search')
def search_results():
    query = request.args.get('q', '')
    results = []
    if query:
        results = Temple.query.filter(
            Temple.is_active == True,
            (Temple.name.ilike(f'%{query}%') |
             Temple.deity.ilike(f'%{query}%') |
             Temple.city.ilike(f'%{query}%') |
             Temple.state.ilike(f'%{query}%') |
             Temple.description.ilike(f'%{query}%'))
        ).all()
    return render_template('search_results.html', results=results, query=query)


@app.route('/accommodations')
def accommodations():
    state_filter = request.args.get('state', '')
    type_filter = request.args.get('type', '')
    query = Accommodation.query.filter_by(is_active=True)
    if state_filter:
        query = query.filter(Accommodation.state == state_filter)
    if type_filter:
        query = query.filter(Accommodation.type == type_filter)
    accommodations = query.all()
    states = db.session.query(Accommodation.state).distinct().order_by(Accommodation.state).all()
    types = db.session.query(Accommodation.type).distinct().all()
    return render_template('accommodations.html',
                           accommodations=accommodations,
                           states=[s[0] for s in states if s[0]],
                           types=[t[0] for t in types if t[0]],
                           state_filter=state_filter,
                           type_filter=type_filter)


@app.route('/travel-packages')
def travel_packages():
    packages = TravelPackage.query.filter_by(is_active=True).all()
    return render_template('travel_packages.html', packages=packages)


@app.route('/travel-agents')
def travel_agents():
    state_filter = request.args.get('state', '')
    query = TravelAgent.query.filter_by(is_active=True)
    if state_filter:
        query = query.filter(TravelAgent.state == state_filter)
    agents = query.all()
    states = db.session.query(TravelAgent.state).distinct().order_by(TravelAgent.state).all()
    return render_template('travel_agents.html',
                           agents=agents,
                           states=[s[0] for s in states if s[0]],
                           state_filter=state_filter)


@app.route('/recommendations')
def recommendations():
    state_filter = request.args.get('state', '')
    deity_filter = request.args.get('deity', '')
    query = Temple.query.filter_by(is_active=True).order_by(Temple.rating.desc())
    if state_filter:
        query = query.filter(Temple.state == state_filter)
    if deity_filter:
        query = query.filter(Temple.deity.ilike(f'%{deity_filter}%'))
    recommended = query.limit(12).all()
    states = db.session.query(Temple.state).distinct().order_by(Temple.state).all()
    deities = db.session.query(Temple.deity).distinct().order_by(Temple.deity).all()
    return render_template('recommendations.html',
                           recommended=recommended,
                           states=[s[0] for s in states if s[0]],
                           deities=[d[0] for d in deities if d[0]],
                           state_filter=state_filter,
                           deity_filter=deity_filter)


@app.route('/about')
def about():
    total_temples = Temple.query.filter_by(is_active=True).count()
    total_users = User.query.filter_by(is_active=True).count()
    total_reviews = Review.query.filter_by(is_approved=True).count()
    states = db.session.query(Temple.state).distinct().count()
    return render_template('about.html',
                           total_temples=total_temples,
                           total_users=total_users,
                           total_reviews=total_reviews,
                           states=states)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        msg = ContactMessage(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        user = User(username=username, email=email,
                    full_name=request.form.get('full_name', ''))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    user_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    user_favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    user_trips = TripPlan.query.filter_by(user_id=current_user.id).order_by(TripPlan.created_at.desc()).all()
    return render_template('profile.html',
                           user_reviews=user_reviews,
                           user_favorites=user_favorites,
                           user_trips=user_trips)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', '')
        current_user.phone = request.form.get('phone', '')
        current_user.city = request.form.get('city', '')
        current_user.state = request.form.get('state', '')
        current_user.bio = request.form.get('bio', '')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html')


# ─────────────────────────────────────────
# REVIEW ROUTES
# ─────────────────────────────────────────

@app.route('/temple/<int:temple_id>/review', methods=['POST'])
@login_required
def add_review(temple_id):
    existing = Review.query.filter_by(temple_id=temple_id, user_id=current_user.id).first()
    if existing:
        flash('You have already reviewed this temple.', 'warning')
        return redirect(url_for('temple_detail', temple_id=temple_id))
    review = Review(
        temple_id=temple_id,
        user_id=current_user.id,
        rating=int(request.form.get('rating', 5)),
        title=request.form.get('title', ''),
        content=request.form.get('content', ''),
        visit_date=request.form.get('visit_date', '')
    )
    db.session.add(review)
    db.session.commit()
    update_temple_rating(temple_id)
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('temple_detail', temple_id=temple_id))


@app.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('index'))
    temple_id = review.temple_id
    db.session.delete(review)
    db.session.commit()
    update_temple_rating(temple_id)
    flash('Review deleted.', 'info')
    return redirect(url_for('temple_detail', temple_id=temple_id))


# ─────────────────────────────────────────
# FAVORITES ROUTES
# ─────────────────────────────────────────

@app.route('/favorite/toggle/<int:temple_id>', methods=['POST'])
@login_required
def toggle_favorite(temple_id):
    existing = Favorite.query.filter_by(user_id=current_user.id, temple_id=temple_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed'})
    fav = Favorite(user_id=current_user.id, temple_id=temple_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'status': 'added'})


@app.route('/favorites')
@login_required
def favorites():
    favs = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.added_at.desc()).all()
    return render_template('favorites.html', favorites=favs)


# ─────────────────────────────────────────
# TRIP PLANNER ROUTES
# ─────────────────────────────────────────

@app.route('/planner')
@login_required
def planner():
    trips = TripPlan.query.filter_by(user_id=current_user.id).order_by(TripPlan.created_at.desc()).all()
    all_temples = Temple.query.filter_by(is_active=True).order_by(Temple.name).all()
    return render_template('planner.html', trips=trips, all_temples=all_temples)


@app.route('/planner/create', methods=['POST'])
@login_required
def create_trip():
    trip = TripPlan(
        user_id=current_user.id,
        name=request.form.get('name'),
        start_date=request.form.get('start_date'),
        end_date=request.form.get('end_date'),
        notes=request.form.get('notes', ''),
        temples_list=json.dumps(request.form.getlist('temples'))
    )
    db.session.add(trip)
    db.session.commit()
    flash('Trip plan created!', 'success')
    return redirect(url_for('planner'))


@app.route('/planner/<int:trip_id>/delete', methods=['POST'])
@login_required
def delete_trip(trip_id):
    trip = TripPlan.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('planner'))
    db.session.delete(trip)
    db.session.commit()
    flash('Trip deleted.', 'info')
    return redirect(url_for('planner'))


# ─────────────────────────────────────────
# ADMIN ROUTES
# ─────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():

    stats = {
        'temples': Temple.query.count(),
        'users': User.query.count(),
        'reviews': Review.query.count(),
        'contacts': ContactMessage.query.filter_by(is_read=False).count(),
        'packages': TravelPackage.query.count(),
        'agents': TravelAgent.query.count(),
    }

    recent_users = User.query.order_by(
        User.joined_date.desc()
    ).limit(5).all()

    recent_reviews = Review.query.order_by(
        Review.created_at.desc()
    ).limit(5).all()

    temples = Temple.query.all()

    top_temples = Temple.query.order_by(
    Temple.review_count.desc()  
).limit(5).all()

    return render_template(
        'dashboard.html',
        temple_count=stats['temples'],
        user_count=stats['users'],
        review_count=stats['reviews'],
        contact_count=stats['contacts'],
        recent_users=recent_users,
        recent_reviews=recent_reviews,
        temples=temples,
        top_temples=top_temples
    )

@app.route('/admin/temples')
@login_required
@admin_required
def admin_temples():
    temples = Temple.query.order_by(Temple.created_at.desc()).all()
    return render_template('temple_form.html', temples=temples, temple=None)



@app.route('/admin/temple/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_temple():
    if request.method == 'POST':

        # ================= IMAGE UPLOAD (PASTE HERE) =================
        image_file = request.files.get('image')

        filename = None
        if image_file and image_file.filename != '':
            from werkzeug.utils import secure_filename
            import os

            filename = secure_filename(image_file.filename)

            image_path = os.path.join('static/images', filename)
            image_file.save(image_path)

        # ================= TEMPLE CREATE =================
        temple = Temple(
            name=request.form.get('name'),
            deity=request.form.get('deity'),
            location=request.form.get('location'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            description=request.form.get('description'),
            history=request.form.get('history'),
            significance=request.form.get('significance'),
            architecture_style=request.form.get('architecture_style'),
            temple_type=request.form.get('temple_type'),
            built_year=request.form.get('built_year'),
            opening_time=request.form.get('opening_time'),
            closing_time=request.form.get('closing_time'),
            entry_fee=request.form.get('entry_fee'),
            dress_code=request.form.get('dress_code'),
            best_time_to_visit=request.form.get('best_time_to_visit'),
            festivals=request.form.get('festivals'),
            nearest_railway=request.form.get('nearest_railway'),
            nearest_airport=request.form.get('nearest_airport'),
            latitude=float(request.form.get('latitude') or 0),
            longitude=float(request.form.get('longitude') or 0),

            # ⭐ IMPORTANT LINE
            image=filename
        )

        db.session.add(temple)
        db.session.commit()

        flash('Temple added successfully!', 'success')
        return redirect(url_for('admin_temples'))

    return render_template('temple_form.html', temple=None)


@app.route('/admin/temple/edit/<int:temple_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_temple(temple_id):
    temple = Temple.query.get_or_404(temple_id)

    if request.method == 'POST':
        temple.name = request.form.get('name')
        temple.deity = request.form.get('deity')
        temple.location = request.form.get('location')
        temple.city = request.form.get('city')
        temple.state = request.form.get('state')
        temple.description = request.form.get('description')
        temple.history = request.form.get('history')
        temple.significance = request.form.get('significance')
        temple.architecture_style = request.form.get('architecture_style')
        temple.temple_type = request.form.get('temple_type')
        temple.built_year = request.form.get('built_year')
        temple.opening_time = request.form.get('opening_time')
        temple.closing_time = request.form.get('closing_time')
        temple.dress_code = request.form.get('dress_code')
        temple.entry_fee = request.form.get('entry_fee')
        temple.best_time_to_visit = request.form.get('best_time_to_visit')
        temple.nearest_railway = request.form.get('nearest_railway')
        temple.nearest_airport = request.form.get('nearest_airport')
        temple.festivals = request.form.get('festivals')
        temple.is_featured = bool(request.form.get('is_featured'))

        db.session.commit()

        flash('Temple updated!', 'success')
        return redirect(url_for('admin_temples'))

    return render_template(
        'temple_form.html',
        temple=temple,
        temples=Temple.query.all()
    )

@app.route('/admin/temple/delete/<int:temple_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_temple(temple_id):
    temple = Temple.query.get_or_404(temple_id)
    db.session.delete(temple)
    db.session.commit()
    flash('Temple deleted.', 'info')
    return redirect(url_for('admin_temples'))


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.joined_date.desc()).all()
    return render_template('users.html', users=users)


@app.route('/admin/user/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin_users'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {"activated" if user.is_active else "deactivated"}.', 'info')
    return redirect(url_for('admin_users'))


@app.route('/admin/reviews')
@login_required
@admin_required
def admin_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('reviews.html', reviews=reviews)


@app.route('/admin/review/toggle/<int:review_id>', methods=['POST'])
@login_required
@admin_required
def admin_toggle_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = not review.is_approved
    db.session.commit()
    update_temple_rating(review.temple_id)
    flash('Review status updated.', 'info')
    return redirect(url_for('admin_reviews'))


@app.route('/admin/contacts')
@login_required
@admin_required
def admin_contacts():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    ContactMessage.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('contacts.html', messages=messages)


@app.route('/admin/announcements')
@login_required
@admin_required
def admin_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcements.html',announcements=announcements)


@app.route('/admin/announcement/add', methods=['POST'])
@login_required
@admin_required
def admin_add_announcement():
    ann = Announcement(
        title=request.form.get('title'),
        content=request.form.get('content'),
        type=request.form.get('type', 'info')
    )
    db.session.add(ann)
    db.session.commit()
    flash('Announcement added!', 'success')
    return redirect(url_for('admin_announcements'))


@app.route('/admin/announcement/delete/<int:ann_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('admin_announcements'))


@app.route("/gallery")
def gallery():
    images = os.listdir("static/images/gallery")
    return render_template("gallery.html", images=images)
# ─────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('404.html'), 500


# ─────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────

def seed_data():
    if Temple.query.count() > 0:
        return

    # Admin user
    admin = User(username='admin', email='sthalapurana27@gmail.com',
                 full_name='Site Administrator', is_admin=True)
    admin_pw = os.getenv('ADMIN_PASSWORD') or secrets.token_urlsafe(10)
    admin.set_password(admin_pw)
    print(f"Admin login: sthalapurana27@gmail.com / {admin_pw}")
    db.session.add(admin)

    # Sample user
    user1 = User(username='devotee1', email='devotee@example.com',
                 full_name='Ramesh Kumar', city='Chennai', state='Tamil Nadu')
    user1.set_password(secrets.token_urlsafe(10))
    db.session.add(user1)

    temples_data = [
        {
            'name': 'Brihadeeswarar Temple',
            'deity': 'Lord Shiva',
            'location': 'Gangaikonda Cholapuram Road, Thanjavur',
            'city': 'Thanjavur',
            'state': 'Tamil Nadu',
            'description': 'The Brihadeeswarar Temple, also known as Peruvudaiyar Kovil, is a Hindu temple dedicated to Shiva located in Thanjavur, Tamil Nadu, India. It is one of the largest temples in India and is a fine example of Dravidian architecture.',
            'history': 'Built by Raja Raja Chola I between 1003 and 1010 CE, this temple is a masterpiece of Tamil architecture. The temple was built as part of Raja Raja Chola\'s grand vision to create a monument that would outlast centuries.',
            'significance': 'This UNESCO World Heritage Site is considered one of the greatest glories of Indian temple architecture. The 216-foot vimana (tower) is one of the tallest in the world.',
            'architecture_style': 'Dravidian',
            'temple_type': 'Shaiva',
            'built_year': '1010 CE',
            'opening_time': '6:00 AM',
            'closing_time': '8:30 PM',
            'dress_code': 'Traditional attire preferred. Men must remove shirts inside sanctum.',
            'entry_fee': 'Free (₹50 for camera)',
            'best_time_to_visit': 'October to March',
            'nearest_railway': 'Thanjavur Junction (2 km)',
            'nearest_airport': 'Tiruchirappalli International Airport (55 km)',
            'festivals': 'Shivaratri, Karthigai Deepam, Brahmotsavam',
            'is_featured': True,
            'latitude': 10.7828,
            'longitude': 79.1318,
        },
        {
            'name': 'Meenakshi Amman Temple',
            'deity': 'Goddess Meenakshi & Lord Sundareswarar',
            'location': 'Madurai City Center',
            'city': 'Madurai',
            'state': 'Tamil Nadu',
            'description': 'The Meenakshi Amman Temple is a historic Hindu temple located in Madurai, Tamil Nadu, India. It is dedicated to the goddess Meenakshi, a form of Parvati, and her consort Sundareswarar, a form of Shiva.',
            'history': 'The original temple was built by Kulasekara Pandya, but the major construction and renovation was carried out during the 16th–17th centuries by Nayaks.',
            'significance': 'One of the most important pilgrimage sites in India, the temple attracts about 15,000–20,000 visitors daily. Its twelve gopurams (gateway towers) are covered with thousands of colorful stone figures.',
            'architecture_style': 'Dravidian',
            'temple_type': 'Shakta-Shaiva',
            'built_year': '7th Century (renovated 17th Century)',
            'opening_time': '5:00 AM',
            'closing_time': '9:30 PM',
            'dress_code': 'Traditional attire. Dhoti for men, saree/salwar for women.',
            'entry_fee': 'Free (₹50 for camera, ₹100 for video)',
            'best_time_to_visit': 'October to March',
            'nearest_railway': 'Madurai Junction (1 km)',
            'nearest_airport': 'Madurai Airport (12 km)',
            'festivals': 'Chithirai Festival (April-May), Shivaratri, Navaratri',
            'is_featured': True,
            'latitude': 9.9195,
            'longitude': 78.1193,
        },
        {
            'name': 'Tirupati Balaji Temple',
            'deity': 'Lord Venkateswara (Vishnu)',
            'location': 'Tirumala Hills',
            'city': 'Tirupati',
            'state': 'Andhra Pradesh',
            'description': 'The Tirumala Venkateswara Temple is a famous Hindu temple situated on the hills of Tirumala at Tirupati in Andhra Pradesh. The temple is dedicated to Venkateswara, an incarnation of Vishnu.',
            'history': 'The temple has a history of over 1000 years. References to this temple appear in Sangam literature. It is one of the richest temples in the world.',
            'significance': 'The richest and most visited temple in the world, receiving over 50,000–100,000 pilgrims daily. Annual income exceeds ₹3000 crore.',
            'architecture_style': 'Dravidian',
            'temple_type': 'Vaishnava',
            'built_year': '300 CE (approx.)',
            'opening_time': '2:30 AM',
            'closing_time': '1:30 AM (next day)',
            'dress_code': 'Traditional only. Men: Dhoti/Pyjama. Women: Saree/Half-saree/Salwar',
            'entry_fee': 'Free (Special Darshan ₹300)',
            'best_time_to_visit': 'September to February',
            'nearest_railway': 'Tirupati Railway Station (20 km)',
            'nearest_airport': 'Tirupati Airport (15 km)',
            'festivals': 'Brahmotsavam (September), Vaikunta Ekadashi',
            'is_featured': True,
            'latitude': 13.6832,
            'longitude': 79.3477,
        },
        {
            'name': 'Kashi Vishwanath Temple',
            'deity': 'Lord Shiva',
            'location': 'Vishwanath Gali, Varanasi',
            'city': 'Varanasi',
            'state': 'Uttar Pradesh',
            'description': 'Kashi Vishwanath Temple is one of the most famous Hindu temples dedicated to Lord Shiva. It is located in Vishwanath Gali of Varanasi, Uttar Pradesh, India.',
            'history': 'The original Vishwanath temple was demolished several times and rebuilt. The current temple was built by Maharani Ahilyabai Holkar of Indore in 1780.',
            'significance': 'One of the twelve Jyotirlingas of Lord Shiva, this temple is considered the holiest Shiva temple in the world. It stands on the western bank of the holy Ganges.',
            'architecture_style': 'Nagara',
            'temple_type': 'Shaiva',
            'built_year': '1780 CE (current structure)',
            'opening_time': '3:00 AM',
            'closing_time': '11:00 PM',
            'dress_code': 'Traditional attire. No jeans/shorts.',
            'entry_fee': 'Free',
            'best_time_to_visit': 'October to March',
            'nearest_railway': 'Varanasi Junction (3 km)',
            'nearest_airport': 'Lal Bahadur Shastri Airport (25 km)',
            'festivals': 'Mahashivaratri, Dev Deepawali, Kashi Utsav',
            'is_featured': True,
            'latitude': 25.3109,
            'longitude': 83.0107,
        },
        {
            'name': 'Golden Temple (Sri Harmandir Sahib)',
            'deity': 'Sri Guru Granth Sahib',
            'location': 'Golden Temple Road',
            'city': 'Amritsar',
            'state': 'Punjab',
            'description': 'The Harmandir Sahib, informally referred to as the Golden Temple, is a gurdwara located in the city of Amritsar, Punjab, India. It is the preeminent spiritual site of Sikhism.',
            'history': 'The construction of the Harmandir Sahib was started by the fifth Sikh Guru, Guru Arjan Dev. The present building was completed in 1604.',
            'significance': 'The holiest gurdwara and one of the most visited pilgrimage sites in the world. The free langar (community kitchen) serves 100,000 meals daily.',
            'architecture_style': 'Sikh Architecture',
            'temple_type': 'Sikh Gurdwara',
            'built_year': '1604 CE',
            'opening_time': '4:00 AM',
            'closing_time': '11:00 PM',
            'dress_code': 'Head must be covered. Remove shoes. No tobacco or alcohol.',
            'entry_fee': 'Free',
            'best_time_to_visit': 'October to March',
            'nearest_railway': 'Amritsar Junction (2 km)',
            'nearest_airport': 'Sri Guru Ram Dass Jee International Airport (11 km)',
            'festivals': 'Guru Nanak Jayanti, Baisakhi, Diwali',
            'is_featured': True,
            'latitude': 31.6200,
            'longitude': 74.8765,
        },
        {
            'name': 'Somnath Temple',
            'deity': 'Lord Shiva',
            'location': 'Prabhas Patan, Veraval',
            'city': 'Somnath',
            'state': 'Gujarat',
            'description': 'Somnath Temple is a Hindu temple located in Prabhas Patan near Veraval in Saurashtra on the western coast of Gujarat, India. It is one of the most sacred pilgrimage sites.',
            'history': 'The Somnath temple has been destroyed and reconstructed several times. The current structure was built in 1951 under the patronage of Sardar Vallabhbhai Patel.',
            'significance': 'First among the twelve Jyotirlinga shrines of Shiva. Located at the coast where three rivers — Kapila, Hiran, and Saraswati — meet the Arabian Sea.',
            'architecture_style': 'Chalukya',
            'temple_type': 'Shaiva',
            'built_year': '1951 CE (current structure)',
            'opening_time': '6:00 AM',
            'closing_time': '9:30 PM',
            'dress_code': 'Traditional attire recommended.',
            'entry_fee': 'Free (Light & Sound Show ₹25)',
            'best_time_to_visit': 'November to February',
            'nearest_railway': 'Veraval Railway Station (7 km)',
            'nearest_airport': 'Diu Airport (63 km)',
            'festivals': 'Mahashivaratri, Kartik Purnima',
            'is_featured': True,
            'latitude': 20.8879,
            'longitude': 70.4013,
        },
        {
            'name': 'Jagannath Temple',
            'deity': 'Lord Jagannath (Vishnu)',
            'location': 'Grand Road, Puri',
            'city': 'Puri',
            'state': 'Odisha',
            'description': 'The Jagannath Temple is a famous Hindu temple dedicated to Lord Jagannath, a form of Vishnu, in Puri, Odisha, India. It is considered one of the Char Dham pilgrimage sites.',
            'history': 'The present temple was constructed in the 12th century by the Eastern Ganga king Anantavarman Chodaganga Deva.',
            'significance': 'One of the four holy dhams of Hinduism. The Rath Yatra (chariot festival) is one of the most attended religious events in India.',
            'architecture_style': 'Kalinga',
            'temple_type': 'Vaishnava',
            'built_year': '12th Century CE',
            'opening_time': '5:00 AM',
            'closing_time': '12:00 AM',
            'dress_code': 'Traditional attire. Non-Hindus not permitted inside.',
            'entry_fee': 'Free',
            'best_time_to_visit': 'October to February',
            'nearest_railway': 'Puri Railway Station (2 km)',
            'nearest_airport': 'Biju Patnaik International Airport (60 km)',
            'festivals': 'Rath Yatra, Snana Yatra, Bahuda Yatra',
            'is_featured': False,
            'latitude': 19.8047,
            'longitude': 85.8316,
        },
        {
            'name': 'Vaishno Devi Temple',
            'deity': 'Goddess Vaishno Devi',
            'location': 'Trikuta Mountains',
            'city': 'Katra',
            'state': 'Jammu & Kashmir',
            'description': 'Vaishno Devi shrine is a cave shrine dedicated to the Hindu goddess Vaishno Devi. It is located in the Trikuta Mountains within the Reasi district of Jammu and Kashmir.',
            'history': 'The legend says that the goddess Vaishno Devi, while being chased by demon Bhairon Nath, took shelter in the cave and eventually killed him.',
            'significance': 'One of the most revered Shakti shrines in India, receiving over 8 million visitors annually. The 14-km trek through scenic mountains is a spiritual journey.',
            'architecture_style': 'Cave Shrine',
            'temple_type': 'Shakta',
            'built_year': 'Ancient (exact date unknown)',
            'opening_time': '5:00 AM',
            'closing_time': '9:00 PM',
            'dress_code': 'Modest traditional attire.',
            'entry_fee': 'Free (Yatra Parchi required)',
            'best_time_to_visit': 'March to October',
            'nearest_railway': 'Katra Railway Station (Padri ki Bawari)',
            'nearest_airport': 'Jammu Airport (50 km)',
            'festivals': 'Navratri (twice yearly), Diwali',
            'is_featured': False,
            'latitude': 32.9904,
            'longitude': 74.9527,
        },
    ]

    for t in temples_data:
        temple = Temple(**t)
        db.session.add(temple)

    db.session.flush()

    # Sample reviews
    temples_list = Temple.query.all()
    for temple in temples_list[:4]:
        review = Review(
            temple_id=temple.id,
            user_id=user1.id,
            rating=5,
            title=f'Amazing experience at {temple.name}',
            content='Truly a divine experience. The temple architecture is breathtaking and the spiritual atmosphere is unmatched. Highly recommended for every devotee.',
            visit_date='2024-01-15'
        )
        db.session.add(review)
        temple.rating = 5.0
        temple.review_count = 1

    # Accommodations
    accommodations = [
        Accommodation(name='Hotel Tamil Nadu', type='Hotel', city='Thanjavur', state='Tamil Nadu',
                      address='Anna Salai, Thanjavur', phone='+91-4362-231325',
                      price_range='₹800 - ₹2500/night', amenities='AC, WiFi, Restaurant, Parking',
                      rating=4.2, nearby_temples='Brihadeeswarar Temple (2 km)'),
        Accommodation(name='Madurai Residency', type='Hotel', city='Madurai', state='Tamil Nadu',
                      address='West Veli Street, Madurai', phone='+91-452-4380000',
                      price_range='₹1500 - ₹5000/night', amenities='AC, WiFi, Pool, Restaurant, Spa',
                      rating=4.5, nearby_temples='Meenakshi Amman Temple (0.5 km)'),
        Accommodation(name='TTD Guest House', type='Guest House', city='Tirupati', state='Andhra Pradesh',
                      address='Tirumala Hills, Tirupati', phone='+91-877-2234567',
                      price_range='₹500 - ₹1500/night', amenities='AC, Vegetarian Restaurant, Darshan Booking',
                      rating=4.0, nearby_temples='Tirupati Balaji Temple (1 km)'),
        Accommodation(name='Varanasi Dharamsala', type='Dharamsala', city='Varanasi', state='Uttar Pradesh',
                      address='Dashashwamedh Ghat Road', phone='+91-542-2391234',
                      price_range='₹200 - ₹800/night', amenities='Basic Amenities, Ghat View, Pure Veg Kitchen',
                      rating=3.8, nearby_temples='Kashi Vishwanath Temple (0.3 km)'),
    ]
    for acc in accommodations:
        db.session.add(acc)

    # Travel packages
    packages = [
        TravelPackage(name='South India Temple Tour', description='Explore the magnificent temples of Tamil Nadu and Andhra Pradesh',
                      duration='7 Days / 6 Nights', price=15999,
                      includes='Accommodation, Transportation, Guide, Meals',
                      temples_covered='Brihadeeswarar, Meenakshi Amman, Tirupati Balaji, Rameshwaram',
                      start_location='Chennai', difficulty='Easy', group_size='10-20 persons'),
        TravelPackage(name='Char Dham Yatra', description='Complete the sacred Char Dham pilgrimage - one of the most revered journeys in Hinduism',
                      duration='14 Days / 13 Nights', price=35000,
                      includes='Accommodation, Transportation, Guide, Puja arrangements',
                      temples_covered='Badrinath, Kedarnath, Gangotri, Yamunotri',
                      start_location='Delhi/Haridwar', difficulty='Moderate', group_size='15-25 persons'),
        TravelPackage(name='North India Spiritual Tour', description='Visit the most sacred temples of North India',
                      duration='10 Days / 9 Nights', price=24999,
                      includes='Accommodation, AC Transportation, Guide, Breakfast',
                      temples_covered='Kashi Vishwanath, Vaishno Devi, Golden Temple, Akshardham',
                      start_location='Delhi', difficulty='Easy', group_size='10-15 persons'),
    ]
    for pkg in packages:
        db.session.add(pkg)

    # Travel agents
    agents = [
        TravelAgent(name='Rajesh Sharma', company='Divine Journeys Pvt Ltd',
                    city='Chennai', state='Tamil Nadu', phone='+91-98765-43210',
                    email='rajesh@divinejourneys.com', specialization='South India Temples, Tamil Nadu Circuit',
                    experience_years=15, rating=4.8, is_verified=True),
        TravelAgent(name='Priya Nair', company='Sacred Trails',
                    city='Tirupati', state='Andhra Pradesh', phone='+91-87654-32109',
                    email='priya@sacredtrails.com', specialization='Tirupati & AP Temple Tours',
                    experience_years=10, rating=4.6, is_verified=True),
        TravelAgent(name='Amit Singh', company='Kashi Pilgrim Services',
                    city='Varanasi', state='Uttar Pradesh', phone='+91-76543-21098',
                    email='amit@kashipilgrim.com', specialization='North India, Char Dham, Kashi',
                    experience_years=20, rating=4.9, is_verified=True),
    ]
    for agent in agents:
        db.session.add(agent)

    # Announcements
    ann = Announcement(
        title='Welcome to Sthala Purana!',
        content='Discover the divine heritage of India\'s sacred temples. Plan your pilgrimage with us.',
        type='info'
    )
    db.session.add(ann)

    db.session.commit()
    print("✓ Seed data created successfully!")

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email not found.', 'danger')
            return redirect(url_for('reset_password'))

        user.password_hash = generate_password_hash(password)

        db.session.commit()

        flash('Password updated successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)

