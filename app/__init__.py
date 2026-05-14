from datetime import datetime
from flask import Flask, render_template
from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
    login_manager.login_message_category = 'warning'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Context processors
    @app.context_processor
    def inject_globals():
        from app.models import Brand
        brands = Brand.query.order_by(Brand.name).all()
        return dict(nav_brands=brands, now=datetime.utcnow())

    # Register blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.rackets import rackets_bp
    app.register_blueprint(rackets_bp)

    from app.blueprints.brands import brands_bp
    app.register_blueprint(brands_bp)

    from app.blueprints.blog import blog_bp
    app.register_blueprint(blog_bp)

    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Create tables and auto-seed if empty
    with app.app_context():
        db.create_all()
        _auto_seed()

    return app


def _auto_seed():
    """Seed database automatically if it has no data."""
    from app.models import Brand
    try:
        if Brand.query.count() == 0:
            import subprocess, sys
            subprocess.run([sys.executable, 'seed.py'], check=True)
    except Exception:
        pass
