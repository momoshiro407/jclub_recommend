import json
from pathlib import Path
from flask import current_app
from ..extensions import db
from ..models import Club, Question, Choice, QuestionChoiceWeight, Prefecture, Stadium


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
        short_name = c.get('short_name', '').strip()
        division = int(c.get('division', 0))
        location = c.get('location', '').strip()
        image_url = c.get('image_url', '').strip()
        team_color = c.get('team_color', '').strip()
        website_url = c.get('website_url', '').strip()
        description = c.get('description', '').strip()
        prefcture_id = int(c.get('prefecture_id', 1))
        supporter_heat = c.get('supporter_heat', 0)
        rivalry_intensity_preference = c.get(
            'rivalry_intensity_preference', 0)
        main_stadium_id = c.get('main_stadium_id', 1)
        win_j1 = c.get('win_j1', 0)
        win_j2 = c.get('win_j2', 0)
        win_j3 = c.get('win_j3', 0)
        win_emperor = c.get('win_emperor', 0)
        win_levain = c.get('win_levain', 0)
        win_acl = c.get('win_acl', 0)
        win_acl2 = c.get('win_acl2', 0)

        # nameをユニークキーとしてupsert
        club = Club.query.filter_by(name=name).first()
        if club is None:
            db.session.add(
                Club(name=name, short_name=short_name, division=division, location=location, image_url=image_url, team_color=team_color,
                     website_url=website_url, description=description, prefecture_id=prefcture_id, supporter_heat=supporter_heat,
                     rivalry_intensity_preference=rivalry_intensity_preference, main_stadium_id=main_stadium_id,
                     win_j1=win_j1, win_j2=win_j2, win_j3=win_j3, win_emperor=win_emperor, win_levain=win_levain,
                     win_acl=win_acl, win_acl2=win_acl2))
        else:
            club.short_name = short_name
            club.division = division
            club.location = location
            club.image_url = image_url
            club.team_color = team_color
            club.website_url = website_url
            club.description = description
            club.prefecture_id = prefcture_id
            club.supporter_heat = supporter_heat
            club.rivalry_intensity_preference = rivalry_intensity_preference
            club.main_stadium_id = main_stadium_id
            club.win_j1 = win_j1
            club.win_j2 = win_j2
            club.win_j3 = win_j3
            club.win_emperor = win_emperor
            club.win_levain = win_levain
            club.win_acl = win_acl
            club.win_acl2 = win_acl2

    db.session.commit()
    print(f'Seed completed: clubs inserted')


def run_seed_stadiums():
    """ seed_stadiums_2025.jsonを読み込み、Stadiumのシードデータを投入する。
        nameをユニークキーとしてupsertに対応可能。
    """
    path = Path(current_app.root_path) / 'seeds' / 'seed_stadiums_2025.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    for s in payload:
        name = s.get('name', '').strip()
        latitude = int(s.get('latitude', 0))
        longitude = int(s.get('longitude', 0))
        capacity = int(s.get('capacity', 0))
        accessibility = int(s.get('accessibility', 0))

        # nameをユニークキーとしてupsert
        stadium = Stadium.query.filter_by(name=name).first()
        if stadium is None:
            db.session.add(
                Stadium(name=name, latitude=latitude, longitude=longitude, capacity=capacity, accessibility=accessibility))
        else:
            stadium.latitude = latitude
            stadium.longitude = longitude
            stadium.capacity = capacity
            stadium.accessibility = accessibility

    db.session.commit()
    print(f'Seed completed: stadiums inserted')


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


def run_seed_prefectures():
    """seed_prefectures.jsonを読み込み、Prefectureのシードデータを投入する。
        insertのみ対応。
    """
    path = Path(current_app.root_path) / 'seeds' / 'seed_prefectures.json'
    with open(path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    # 既存データを全削除
    Prefecture.query.delete()
    for pref in payload:
        db.session.add(Prefecture(id=pref.get('id'),
                       name=pref.get('name', '').strip()))

    db.session.commit()
    print(f'Seed completed: prefectures (replaced all)')


def migrate_stadiums():
    """Clubデータからスタジアム関係のカラムを抽出しStadiumテーブルに移行する。
    """
    clubs = Club.query.order_by(Club.id.asc()).all()

    for club in clubs:
        if not club.main_stadium_name:
            continue

        # 既存のスタジアムを検索（同名スタジアムの重複回避）
        stadium = Stadium.query.filter_by(name=club.main_stadium_name).first()

        # 存在しない場合は新規作成
        if not stadium:
            stadium = Stadium(
                name=club.main_stadium_name,
                latitude=club.stadium_latitude,
                longitude=club.stadium_longitude,
                capacity=club.stadium_capacity,
                accessibility=club.stadium_access
            )
            db.session.add(stadium)
            db.session.flush()  # ID発行

        # Clubに紐づけ
        club.main_stadium_id = stadium.id

    db.session.commit()
    print('Stadiumデータの移行と紐づけ完了')


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
