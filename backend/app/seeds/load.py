import json
from pathlib import Path
from flask import current_app
from ..extensions import db
from ..models import Club, Question, Choice, QuestionChoiceWeight


def run_seed_clubs():
    """ seed_clubs_2025.jsonを読み込み、Clubのシードデータを投入する。
        nameをユニークキーとしてupsertに対応可能。
    """
    path = Path(current_app.root_path) / 'seeds' / 'seed_clubs_2025.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    for c in payload:
        name = c.get('name', '').strip()
        division = int(c.get('division', 0))
        location = c.get('location', '').strip()

        # nameをユニークキーとしてupsert
        club = Club.query.filter_by(name=name).first()
        if club is None:
            db.session.add(
                Club(name=name, division=division, location=location))
        else:
            club.division = division
            club.location = location

    db.session.commit()
    print(f'Seed completed: clubs inserted')


def run_seed_questions():
    """seed_questions.jsonを読み込み、Question/Choiceのシードデータを投入する。
        insertのみ対応。
    """
    path = Path(current_app.root_path) / 'seeds' / 'seed_questions.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    # 既存データを全削除
    Choice.query.delete()
    Question.query.delete()
    db.session.commit()

    for q in payload:
        question = Question(
            text=q.get('text').strip(),
            order=q.get('order', 0)
        )
        db.session.add(question)
        db.session.flush()  # question.id を取得

        for c in q.get('choices', []):
            db.session.add(Choice(
                question_id=question.id,
                text=c.get('text').strip(),
                order=c.get('order', 0)
            ))

    db.session.commit()
    print(f'Seed completed: questions & choices inserted (replaced all)')


def run_seed_weights():
    """seed_question_choice_weights.jsonを読み込み、質問・選択肢の組に対応する特徴量の重みのデータを投入する。
        insertのみ対応。
    """
    path = Path(current_app.root_path) / 'seeds' / \
        'seed_question_choice_weights.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    # 既存データを全削除
    QuestionChoiceWeight.query.delete()
    db.session.commit()

    for item in payload:
        question = Question.query.filter_by(
            order=item['question_order']).first()
        if not question:
            continue
        choice = Choice.query.filter_by(
            question_id=question.id, order=item['choice_order']).first()
        if not choice:
            continue
        for w in item['weights']:
            db.session.add(
                QuestionChoiceWeight(
                    question_id=question.id,
                    choice_id=choice.id,
                    feature_name=w.get('feature', '').strip(),
                    weight=w.get('weight', 0.0)
                )
            )

    db.session.commit()
    print(f'Seed completed: weight mappings (replaced all)')


def update_club_features():
    """動作確認用にクラブの特徴量を適当に更新
        ダミーデータなので動作確認時のみ使用し、本番運用では使用しない
    """
    # 例: 鹿島アントラーズ
    club = Club.query.filter_by(name="鹿島アントラーズ").first()
    if club:
        club.strength_long_term = 0.9
        club.strength_short_term = 0.8
        club.domestic_titles = 20
        club.popularity_score = 0.9
        club.supporter_heat = 0.95
        club.ticket_availability = 0.3  # 満員率高め → チケット取りにくい
        club.play_style_attack = 0.7
        club.play_style_defense = 0.5

    # 例: 浦和レッズ
    club = Club.query.filter_by(name="浦和レッズ").first()
    if club:
        club.strength_long_term = 0.7
        club.strength_short_term = 0.75
        club.domestic_titles = 8
        club.international_titles = 3
        club.popularity_score = 0.95
        club.supporter_heat = 0.95
        club.ticket_availability = 0.3
        club.play_style_attack = 0.56
        club.play_style_defense = 0.85

    # 例: 川崎フロンターレ
    club = Club.query.filter_by(name="川崎フロンターレ").first()
    if club:
        club.strength_long_term = 0.85
        club.strength_short_term = 0.95
        club.domestic_titles = 10
        club.popularity_score = 0.85
        club.supporter_heat = 0.7
        club.ticket_availability = 0.4
        club.play_style_attack = 0.9
        club.play_style_defense = 0.4

    # 例: ベガルタ仙台
    club = Club.query.filter_by(name="ベガルタ仙台").first()
    if club:
        club.strength_long_term = 0.55
        club.strength_short_term = 0.67
        club.domestic_titles = 0
        club.popularity_score = 0.7
        club.supporter_heat = 0.85
        club.ticket_availability = 0.2
        club.play_style_attack = 0.7
        club.play_style_defense = 0.3

    # 例: 大分トリニータ（アンダードッグ気味）
    club = Club.query.filter_by(name="大分トリニータ").first()
    if club:
        club.strength_long_term = 0.3
        club.strength_short_term = 0.5
        club.domestic_titles = 0
        club.popularity_score = 0.4
        club.supporter_heat = 0.5
        club.ticket_availability = 0.8  # 空席が多め
        club.play_style_attack = 0.5
        club.play_style_defense = 0.6

    db.session.commit()
    print('Update completed: club features updated')
