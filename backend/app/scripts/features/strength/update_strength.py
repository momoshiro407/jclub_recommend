# flask update-strength long
# flask update-strength short
import pandas as pd
import os
from flask import current_app
from pathlib import Path
from sqlalchemy import create_engine, text, table, column
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
LONG_TERM = 'long'
SHORT_TERM = 'short'


def update_strength(term: str):
    if not term in [LONG_TERM, SHORT_TERM]:
        print(f'"term" must be {LONG_TERM} or {SHORT_TERM}')
        return

    # 登録対象の強さスコア
    target_feature = f'strength_{term}_term'

    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'{target_feature}.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')
    # CSV読み込み
    df = pd.read_csv(path)

    engine = create_engine(DATABASE_URL)
    clubs = table('clubs', column('name'), column(f'{target_feature}'))

    with engine.begin() as conn:
        for _, row in df.iterrows():
            club_name = row['club_name']
            strength = float(row[f'{target_feature}']) if not pd.isna(
                row[f'{target_feature}']) else None

            if strength is not None:
                query = text(f"""
                    UPDATE clubs
                    SET {target_feature} = :strength
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'strength': strength,
                        'club_name': club_name,
                    })

    print(f'{target_feature} updated using.')
