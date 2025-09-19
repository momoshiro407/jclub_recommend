from flask import Blueprint, jsonify
from app.models import Question, Choice

bp = Blueprint('questions', __name__)


@bp.route('/', methods=['GET'])
def get_questions():
    questions = Question.query.order_by(Question.order.asc().nullslast()).all()
    data = [
        {
            'id': q.id,
            'text': q.text,
            'order': q.order,
            'choices': [
                {
                    'id': c.id,
                    'text': c.text,
                    'order': c.order
                } for c in q.choices
            ]
        } for q in questions]

    return jsonify({'questions': data})
