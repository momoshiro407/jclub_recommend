import json
from pathlib import Path
from flask import current_app
from ..extensions import db
from ..models import Club


def run_seed():
    path = Path(current_app.root_path) / 'seeds' / 'clubs_2025.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        clubs = json.load(f)

    # upsert: nameをユニークキーとして更新or作成
    for c in clubs:
        name = c['name'].strip()
        division = int(c['division'])
        location = c['location'].strip()

        existing = Club.query.filter_by(name=name).first()
        if existing:
            existing.division = division
            existing.location = location
        else:
            db.session.add(
                Club(name=name, division=division, location=location))

    db.session.commit()
    print(f'Seed completed: {len(clubs)} clubs')
