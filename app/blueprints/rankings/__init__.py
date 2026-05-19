from flask import Blueprint

rankings_bp = Blueprint('rankings', __name__, url_prefix='/bang-xep-hang')

from app.blueprints.rankings import routes
