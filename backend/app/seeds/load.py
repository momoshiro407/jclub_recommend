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
    """questions_2025.jsonを読み込み、Question/Choiceのシードデータを投入する。
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
    """question_choice_weights.jsonを読み込み、質問・選択肢の組に対応する特徴量の重みのデータを投入する。
        insertのみ対応。
    """
    path = Path(current_app.root_path) / 'seeds' / \
        'question_choice_weights.json'
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
