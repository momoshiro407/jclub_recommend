import os
from flask import current_app
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, select, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')

# 所要時間カラムのラベル
WALK = 'walking_time_required'
BUS = 'bus_time_required'

# スコア計算用パラメータ（base, beta）
CALC_PARAMS = {
    WALK: (0.50, 0.50),
    BUS: (0, 0.50),
}

# 徒歩所要時間を採用する閾値（分）
WALKING_TIME_THRESHOLD = 30


def compute_score(df: pd.DataFrame) -> pd.Series:
    score = pd.Series(0.0, index=df.index, dtype='float')

    def normalise(row, type, min_val, max_val):
        time_required = row[type]
        base, beta = CALC_PARAMS[type]
        # min=max（全件同値）のときはnorm=1.0扱い
        if pd.isna(time_required):
            return 0.0
        if max_val == min_val:
            norm_score = 1.0
        else:
            # 所要時間が短いほどスコアが高くなるように正規化
            norm_score = 1.0 - (time_required - min_val) / (max_val - min_val)
        # 念のためクリップ
        norm_score = max(0.0, min(1.0, float(norm_score)))

        return round(base + beta * norm_score, 3)

    # 徒歩採用群：walking<30のみ
    walk_df = df.loc[(df[WALK].notna()) & (
        df[WALK] < WALKING_TIME_THRESHOLD)]
    walk_min = walk_df[WALK].min()
    walk_max = walk_df[WALK].max()
    # バス採用群：walkingがNoneまたはwalking>=30かつbusがあるものだけ
    bus_df = df.loc[(df[WALK].isna()) | (
        df[WALK] >= WALKING_TIME_THRESHOLD) & (df[BUS].notna())]
    bus_min = bus_df[BUS].min()
    bus_max = bus_df[BUS].max()

    # walkは [0.5..1.0]（base=0.5,beta=0.5）、busは [0..0.5]（base=0,beta=0.5）
    if not walk_df.empty:
        score.loc[walk_df.index] = walk_df.apply(
            lambda row: normalise(row, WALK, walk_min, walk_max), axis=1
        )
    if not bus_df.empty:
        score.loc[bus_df.index] = bus_df.apply(
            lambda row: normalise(row, BUS, bus_min, bus_max), axis=1
        )

    return score


def update_accessibility():
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    stadiums = Table('stadiums', metadata, autoload_with=engine)

    # stadiumレコードの中の必要なカラムのみ指定
    select_cols = ['id', 'walking_time_required', 'bus_time_required']
    # キーをもとに stadiums.c からカラムオブジェクトを動的に取得
    columns = [getattr(stadiums.c, key) for key in select_cols]

    with engine.begin() as conn:
        result = conn.execute(select(*columns))
        records = list(result.mappings())
        df = pd.DataFrame(records)
        df['accessibility'] = compute_score(df)
        print(df)

        for _, row in df.iterrows():
            query = text("""
                UPDATE stadiums
                SET accessibility = :accessibility
                WHERE id = :id
            """)
            conn.execute(query, {
                'accessibility': float(row['accessibility']),
                'id': int(row['id'])
            })

    print(f'accessibility updated.')
