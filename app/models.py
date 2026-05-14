import re
import unicodedata
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


def generate_slug(text):
    """Convert Vietnamese text to URL-safe slug."""
    # Normalize unicode characters
    text = unicodedata.normalize('NFD', text)
    # Remove diacritics
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text


# Association table for many-to-many RacketTag
racket_tags = db.Table('racket_tags',
    db.Column('racket_id', db.Integer, db.ForeignKey('rackets.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    blog_posts = db.relationship('BlogPost', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    logo = db.Column(db.String(255))
    description = db.Column(db.Text)
    country = db.Column(db.String(100))
    banner_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    rackets = db.relationship('Racket', backref='brand', lazy='dynamic')

    def __repr__(self):
        return f'<Brand {self.name}>'


class Racket(db.Model):
    __tablename__ = 'rackets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)

    # Specifications
    weight_class = db.Column(db.String(10))  # 3U, 4U, 5U
    balance_type = db.Column(db.String(20))  # head_heavy, even, head_light
    flexibility = db.Column(db.String(20))   # extra_stiff, stiff, medium, flexible, extra_flexible
    frame_material = db.Column(db.String(200))
    shaft_material = db.Column(db.String(200))
    skill_level = db.Column(db.String(20))   # beginner, intermediate, advanced, professional
    price = db.Column(db.Integer)            # Price in VND (thousands)

    # Description
    description = db.Column(db.Text)
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    playing_style = db.Column(db.Text)

    # String tension
    string_tension_min = db.Column(db.Integer)
    string_tension_max = db.Column(db.Integer)

    # Dimensions
    length_mm = db.Column(db.Integer, default=675)

    # Stats
    view_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)

    # SEO
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('RacketImage', backref='racket', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='RacketImage.order')
    tags = db.relationship('Tag', secondary=racket_tags, backref=db.backref('rackets', lazy='dynamic'))
    reviews = db.relationship('Review', backref='racket', lazy='dynamic',
                              cascade='all, delete-orphan')

    def increment_view(self):
        self.view_count = (self.view_count or 0) + 1
        db.session.commit()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def primary_image(self):
        img = self.images.filter_by(is_primary=True).first()
        if not img:
            img = self.images.first()
        return img

    @property
    def weight_class_display(self):
        return self.weight_class or 'N/A'

    @property
    def balance_type_display(self):
        mapping = {
            'head_heavy': 'Nặng đầu',
            'even': 'Cân bằng',
            'head_light': 'Nhẹ đầu'
        }
        return mapping.get(self.balance_type, self.balance_type or 'N/A')

    @property
    def flexibility_display(self):
        mapping = {
            'extra_stiff': 'Siêu cứng',
            'stiff': 'Cứng',
            'medium': 'Trung bình',
            'flexible': 'Mềm',
            'extra_flexible': 'Siêu mềm'
        }
        return mapping.get(self.flexibility, self.flexibility or 'N/A')

    @property
    def skill_level_display(self):
        mapping = {
            'beginner': 'Người mới',
            'intermediate': 'Trung cấp',
            'advanced': 'Nâng cao',
            'professional': 'Chuyên nghiệp'
        }
        return mapping.get(self.skill_level, self.skill_level or 'N/A')

    def __repr__(self):
        return f'<Racket {self.name}>'


class RacketImage(db.Model):
    __tablename__ = 'racket_images'

    id = db.Column(db.Integer, primary_key=True)
    racket_id = db.Column(db.Integer, db.ForeignKey('rackets.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<RacketImage {self.filename}>'


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    featured_image = db.Column(db.String(255))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(300))
    is_published = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def increment_view(self):
        self.view_count = (self.view_count or 0) + 1
        db.session.commit()

    def __repr__(self):
        return f'<BlogPost {self.title}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    racket_id = db.Column(db.Integer, db.ForeignKey('rackets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} for Racket {self.racket_id}>'
