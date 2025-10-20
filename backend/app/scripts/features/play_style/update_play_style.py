import pandas as pd
import os
from flask import current_app
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')


def update_play_style():
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'play_style.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    # CSV読み込み
    df = pd.read_csv(path)

    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            club_name = row['club_name']
            play_style_attack = float(row['play_style_attack']) if not pd.isna(
                row['play_style_attack']) else None
            play_style_defense = float(row['play_style_defense']) if not pd.isna(
                row['play_style_defense']) else None

            if play_style_attack is not None and play_style_defense is not None:
                query = text("""
                    UPDATE clubs
                    SET
                        play_style_attack = :play_style_attack,
                        play_style_defense = :play_style_defense
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'play_style_attack': play_style_attack,
                        'play_style_defense': play_style_defense,
                        'club_name': club_name,
                    })

    print('play_style_attack and play_style_defense updated.')
