from flask import Blueprint, request, jsonify
from ..models import Club
import random

bp = Blueprint('recommend', __name__)

# 仮のクラブデータ
mock_clubs = [
    {
        'id': 1,
        'name': '浦和レッズ',
        'division': 1,
        'location': '埼玉県さいたま市',
        'emblem': 'https://placehold.jp/80x80.png',
        'color': '#E60026',
        'website_url': 'https://www.urawa-reds.co.jp/',
        'description': '熱狂的なファンに支えられる国内屈指の人気クラブ。'
    },
    {
        'id': 2,
        'name': 'ガンバ大阪',
        'division': 1,
        'location': '大阪府吹田市',
        'emblem': 'https://placehold.jp/80x80.png',
        'color': '#0000FF',
        'website_url': 'https://www.gamba-osaka.net/',
        'description': '攻撃的なサッカーと育成力に定評のあるクラブ。'
    },
    {
        'id': 3,
        'name': '鹿島アントラーズ',
        'division': 1,
        'location': '茨城県鹿嶋市',
        'emblem': 'https://placehold.jp/80x80.png',
        'color': '#8B0000',
        'website_url': 'https://www.antlers.co.jp/',
        'description': 'Jリーグ最多優勝を誇る伝統と実力のクラブ。'
    },
    {
        'id': 4,
        'name': 'アルビレックス新潟',
        'division': 1,
        'location': '新潟県新潟市',
        'emblem': 'https://placehold.jp/80x80.png',
        'color': '#FF6600',
        'website_url': 'https://www.albirex.co.jp/',
        'description': '地域密着型でファンとの距離が近いクラブ。'
    },
]


@bp.route('/', methods=['POST'])
def recommend():
    ''' UIからの回答データを受け取り、推薦結果を返すエンドポイント
        モック時はランダムなスコアを割り振る
    '''
    data = request.get_json()
    answers = data.get('answers', [])

    # モック: ランダムスコアを割り振る
    results = []
    for club in mock_clubs:
        results.append({
            'name': club.get('name', ''),
            'division': club.get('division', 0),
            'location': club.get('location', ''),
            'emblem': club.get('emblem', ''),
            'color': club.get('color', '#000000'),
            'description': club.get('description', ''),
            'website_url': club.get('website_url', ''),
            'score': random.randint(60, 100),  # 今はランダムなスコア
        })

    # スコア降順でソートし上位3件返す
    results = sorted(results, key=lambda x: x['score'], reverse=True)[:3]

    return jsonify({'results': results})
