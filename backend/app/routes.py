from flask import Blueprint, jsonify
from .models import Club
from .extensions import db

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.get('/health')
def health():
    return jsonify({'status': 'ok'})


@bp.get('/clubs')
def get_clubs():
    clubs = Club.query.order_by(Club.division, Club.name).all()
    return jsonify([{'id': c.id, 'name': c.name, 'division': c.division, 'location': c.location} for c in clubs])
