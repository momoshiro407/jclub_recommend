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


def update_popularity_score():
    for division in [1, 2, 3]:
        path = Path(current_app.root_path) / 'scripts' / \
            'features' / 'data' / f'popularity_raw_j{division}.csv'
        if not path.exists():
            raise FileNotFoundError(f'{path} not found')

        # CSV読み込み
        df = pd.read_csv(path)
        # 各フォロワー数を合計する
        df['total'] = df['instagram_followers'].fillna(0) \
            + df['twitter_followers'].fillna(0) \
            + df['youtube_subscribers'].fillna(0)

        engine = create_engine(DATABASE_URL)

        with engine.begin() as conn:
            for _, row in df.iterrows():
                club_name = row['club_name']
                total = int(row['total'])

                query = text("""
                    UPDATE clubs
                    SET popularity_score = :popularity_score
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'popularity_score': total,
                        'club_name': club_name,
                    })

    print(f'popularity_score updated.')
