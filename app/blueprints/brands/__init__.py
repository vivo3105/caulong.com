from flask import Blueprint

brands_bp = Blueprint('brands', __name__)

from app.blueprints.brands import routes
