from flask import Blueprint, jsonify

bp = Blueprint('clubs', __name__)


@bp.route('/', methods=['GET'])
def get_clubs():
    return jsonify({'clubs': []})  # 後でDBから返す
