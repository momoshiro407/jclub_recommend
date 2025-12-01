import os
import pandas as pd
from pathlib import Path
from flask import current_app
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, select


# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')


def update_financial_power():
    # 売上高の単位は百万円だが、スコア計算では正規化するため記載の数値をそのまま使用する
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / 'j_kessan-2024.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    # CSV読み込み
    df = pd.read_csv(path)

    engine = create_engine(DATABASE_URL)

    with engine.begin() as conn:
        for _, row in df.iterrows():
            short_name = row['club_name']
            revenue = int(row['revenue']) if not pd.isna(
                row['revenue']) else None

            if revenue is not None:
                query = text("""
                    UPDATE clubs
                    SET financial_power = :financial_power
                    WHERE normalize_alnum(short_name) = normalize_alnum(:short_name)
                """)
                conn.execute(
                    query, {
                        'financial_power': revenue,
                        'short_name': short_name,
                    })

    print(f'financial_power updated.')
