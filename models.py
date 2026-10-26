from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), default="user")
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    bio = db.Column(db.Text)

    avatar = db.Column(
        db.String(200),
        default='default_avatar.png'
    )

    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    joined_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    reviews = db.relationship(
        'Review',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    favorites = db.relationship(
        'Favorite',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    trips = db.relationship(
        'TripPlan',
        backref='user',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

class Temple(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    deity = db.Column(db.String(100))
    location = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    description = db.Column(db.Text)
    history = db.Column(db.Text)
    significance = db.Column(db.Text)
    architecture_style = db.Column(db.String(100))
    temple_type = db.Column(db.String(100))
    built_year = db.Column(db.String(50))
    opening_time = db.Column(db.String(20))
    closing_time = db.Column(db.String(20))
    dress_code = db.Column(db.String(200))
    entry_fee = db.Column(db.String(100))
    best_time_to_visit = db.Column(db.String(200))
    nearest_railway = db.Column(db.String(200))
    nearest_airport = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image = db.Column(db.String(200), default='temple_default.jpg')
    gallery_images = db.Column(db.Text, default='[]')
    festivals = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='temple', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='temple', lazy=True, cascade='all, delete-orphan')


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
   
    temple_id = db.Column(
        db.Integer,
        db.ForeignKey('temple.id'),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    visit_date = db.Column(db.String(50))

    is_approved = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    temple_id = db.Column(db.Integer, db.ForeignKey('temple.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class TripPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    notes = db.Column(db.Text)
    temples_list = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Accommodation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    price_range = db.Column(db.String(100))
    amenities = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    nearby_temples = db.Column(db.Text)
    image = db.Column(db.String(200), default='accommodation_default.jpg')
    is_active = db.Column(db.Boolean, default=True)


class TravelPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    price = db.Column(db.Float)
    includes = db.Column(db.Text)
    temples_covered = db.Column(db.Text)
    start_location = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))
    group_size = db.Column(db.String(50))
    image = db.Column(db.String(200), default='package_default.jpg')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TravelAgent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    specialization = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    rating = db.Column(db.Float, default=0.0)
    image = db.Column(db.String(255))
    status = db.Column(db.String(20),default='pending' )
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

