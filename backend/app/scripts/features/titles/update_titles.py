import os
from flask import current_app
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, select, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')

# 国内大会の重み
DOMESTIC_CONVENTION_WEIGHTS = {
    'win_j1': 1.0,
    'win_j2': 0.5,
    'win_j3': 0.3,
    'win_emperor': 0.75,
    'win_levain': 0.75,
}

# 国際大会の重み
INTERNATIONAL_CONVENTION_WEIGHTS = {
    'win_acl': 1.0,
    'win_acl2': 0.5,
}


def normalize_columns(df: pd.DataFrame, cols: list) -> float:
    """ 0〜1のMin-Maxスケーリングを行う """
    for col in cols:
        print(col)
        min_val, max_val = df[col].min(), df[col].max()
        print(min_val, max_val)

        if pd.isna(min_val) or pd.isna(max_val):
            df[col] = None
        elif max_val == min_val:
            df[col] = 0.5
        else:
            df[col] = ((df[col] - min_val) / (max_val - min_val)).round(3)

    return df


def compute_score(df: pd.DataFrame, weights: dict) -> pd.Series:
    cols = weights.keys()
    for col in cols:
        if col not in df:
            df[col] = 0
    weighted_sum = sum(df[col] * weight for col, weight in weights.items())

    return weighted_sum


def update_titles():
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    clubs = Table('clubs', metadata, autoload_with=engine)

    # clubレコードの中の必要なカラムのみ指定
    select_cols = ['name'] + list(DOMESTIC_CONVENTION_WEIGHTS.keys()) + \
        list(INTERNATIONAL_CONVENTION_WEIGHTS.keys())
    # キーをもとに clubs.c からカラムオブジェクトを動的に取得
    columns = [getattr(clubs.c, key) for key in select_cols]

    with engine.begin() as conn:
        result = conn.execute(select(*columns))
        records = list(result.mappings())

        df = pd.DataFrame(records)
        df['domestic_titles'] = compute_score(
            df, DOMESTIC_CONVENTION_WEIGHTS)
        df['international_titles'] = compute_score(
            df, INTERNATIONAL_CONVENTION_WEIGHTS)

        print(df)

        df = normalize_columns(
            df, ['domestic_titles', 'international_titles'])

        for _, row in df.iterrows():
            club_name = row['name']
            domestic_titles = float(row['domestic_titles']) if not pd.isna(
                row['domestic_titles']) else None
            international_titles = float(row['international_titles']) if not pd.isna(
                row['international_titles']) else None

            # DB更新
            query = text("""
                UPDATE clubs
                SET
                    domestic_titles = :domestic_titles,
                    international_titles = :international_titles
                WHERE normalize_alnum(name) = normalize_alnum(:club_name)
            """)
            conn.execute(
                query, {
                    'domestic_titles': domestic_titles,
                    'international_titles': international_titles,
                    'club_name': club_name,
                })

    print(f'domestic_titles and international_titles updated.')
