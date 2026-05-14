from flask import Blueprint

rackets_bp = Blueprint('rackets', __name__)

from app.blueprints.rackets import routes
