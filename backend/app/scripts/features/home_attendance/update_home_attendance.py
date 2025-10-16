import pandas as pd
import os
from flask import current_app
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
# 使う値を切り替え: 'median' or 'average'
USE_VALUE = 'median'


def update_home_attendance():
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'home_attendance_raw.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    # CSV読み込み
    df = pd.read_csv(path)

    # 切り替え設定
    if USE_VALUE == 'median':
        df['home_attendance'] = df['median_attendance']
    elif USE_VALUE == 'average':
        df['home_attendance'] = df['avg_attendance']

    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            club_name = row['club_name']
            home_attendance = int(row['home_attendance']) if not pd.isna(
                row['home_attendance']) else None

            if home_attendance is not None:
                query = text("""
                    UPDATE clubs
                    SET home_attendance = :home_attendance
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'home_attendance': home_attendance,
                        'club_name': club_name,
                    })

    print(f'home_attendance updated using {USE_VALUE} values.')
