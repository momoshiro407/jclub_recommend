import pandas as pd
import os
from flask import current_app
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')


def update_youth_promotion_score():
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'youth_promotion_score.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    # CSV読み込み
    df = pd.read_csv(path)

    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            club_name = row['club_name']
            youth_promotion_score = int(row['youth_promotion_score']) if not pd.isna(
                row['youth_promotion_score']) else None

            if youth_promotion_score is not None:
                query = text("""
                    UPDATE clubs
                    SET youth_promotion_score = :youth_promotion_score
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'youth_promotion_score': youth_promotion_score,
                        'club_name': club_name,
                    })

    print(f'youth_promotion_score updated using.')
