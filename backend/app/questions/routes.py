from flask import Blueprint, jsonify

bp = Blueprint('questions', __name__)


@bp.route('/', methods=['GET'])
def get_questions():
    # 仮の質問データ
    questions = [
        {
            'id': 1,
            'text': 'サッカー観戦のスタイルは？',
            'choices': [
                {'id': 1, 'text': 'スタジアムで熱狂したい'},
                {'id': 2, 'text': '家でゆったり観たい'}
            ]
        },
        {
            'id': 2,
            'text': '応援したいクラブの地域は？',
            'choices': [
                {'id': 1, 'text': '地元'},
                {'id': 2, 'text': '全国的に有名なクラブ'}
            ]
        },
        {
            'id': 3,
            'text': 'クラブに求めるものは？',
            'choices': [
                {'id': 1, 'text': '強さ'},
                {'id': 2, 'text': '親しみやすさ'}
            ]
        }
    ]
    return jsonify({'questions': questions})
