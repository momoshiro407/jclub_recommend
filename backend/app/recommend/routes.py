from flask import Blueprint, request, jsonify
from ..models import Club, QuestionChoiceWeight

bp = Blueprint('recommend', __name__)


@bp.route('/', methods=['POST'])
def recommend():
    ''' UIからの回答データを受け取り、推薦結果を返すエンドポイント
    '''
    data = request.get_json()
    answers = data.get('answers', [])

    # 全クラブ取得
    clubs = Club.query.all()
    # 回答に対応する全重みを取得し、特徴量ごとに集約
    feature_weights = {}
    for answer in answers:
        qcws = QuestionChoiceWeight.query.filter_by(
            question_id=answer['questionId'], choice_id=answer['choiceId']).all()
        for qcw in qcws:
            feature = qcw.feature_name
            feature_weights[feature] = feature_weights.get(
                feature, 0.0) + qcw.weight

    # 各クラブのスコア算出
    club_scores = {}
    for club in clubs:
        score = 0.0
        for feature, total_weight in feature_weights.items():
            # クラブの該当特徴量を取得（無ければ0）
            value = getattr(club, feature, 0)
            score += value * total_weight
        club_scores[club] = score

    # スコアを0〜100に正規化
    if club_scores:
        min_score = min(club_scores.values())
        max_score = max(club_scores.values())
        # 全スコアを0以上に平行移動
        if min_score < 0:
            for club in club_scores:
                club_scores[club] -= min_score
        # 比率計算（max_scoreが0なら全クラブスコア0のまま）
        if max_score > 0:
            for club in club_scores:
                club_scores[club] = (club_scores[club] / max_score) * 100

    # 上位3クラブを選択
    top_clubs = sorted(club_scores.keys(),
                       key=lambda c: club_scores[c], reverse=True)[:3]

    # 6. レスポンスJSON構築（不足情報はデフォルト埋め）
    results = []
    for club in top_clubs:
        results.append({
            'id': club.id,
            'name': club.name,
            'division': club.division,
            'location': club.location,
            'image_url': club.image_url,
            'team_color': club.team_color,
            'website_url': club.website_url,
            'main_stadium_name': club.main_stadium_name,
            'stadium_latitude': club.stadium_latitude,
            'stadium_longitude': club.stadium_longitude,
            'description': club.description,
            'score': round(club_scores.get(club, 0), 1)
        })
    return jsonify({'results': results})
