# 今シーズンの西暦を指定して実行する
# flak collect-play-style 2025

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from flask import current_app
from pathlib import Path
from dotenv import load_dotenv
from functools import reduce


# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
J_LEAGUE_URL = os.getenv('J_LEAGUE_URL') + \
    '/stats/j{division}/club/{year}/{metric}/'
FOOTBALL_LAB_URL = os.getenv('FOOTBALL_LAB_URL') + \
    '/team_ranking/j{division}'

# JSTATSの指標ラベル
JSTATS_METRICS = {
    'ball_rate': '平均ボール支配率',
    'shoot': 'シュート総数',
    'score': '得点総数',
    'chance_create': 'チャンスクリエイト総数',
    'suffer_shoot': '被シュート総数',
    'lost': '失点総数',
    'block_count': 'ブロック総数',
}

# Football LAB のAGI, KAGIの列番号
AGI_COL = 3

# 攻撃スコア計算のための重み（正規化後）
ATTACK_WEIGHTS = {
    'ball_rate': 0.15,
    'shoot': 0.20,
    'score': 0.15,
    'chance_create': 0.20,
    'agi': 0.30,
}

# 守備スコア計算のための重み（正規化後）
DEFENSE_WEIGHTS = {
    'ball_rate': 0.15,
    'suffer_shoot': 0.25,
    'lost': 0.15,
    'block_count': 0.15,
    'kagi': 0.30,
}

# 逆指標として利用するカラム
REVERSE_INDICATORS = {'ball_rate', 'suffer_shoot', 'lost'}


def fetch_jstats_metric(division: int, year: int) -> pd.DataFrame:
    """ JSTATSから各種指標を取得する """
    metric_dfs = []
    for metric in JSTATS_METRICS:
        url = J_LEAGUE_URL.format(division=division, year=year, metric=metric)
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # 指標ランキングのリストを抽出
        ul = soup.find('ul', class_='ranking_list')
        if not ul:
            return pd.DataFrame()

        result = {'club_name': [], metric: []}
        for li in ul.find_all('li'):
            value = li.select_one(
                'div[class^="ranking_stats"] > p').get_text(strip=True)
            club_name = li.select_one('p.team').get_text(strip=True)
            result['club_name'].append(club_name)
            result[metric].append(float(re.sub(r'[^\d.]+', '', value)))

        metric_dfs.append(pd.DataFrame(result))

    # クラブ名を軸に各指標をマージしたDataFrameを返却
    return reduce(lambda x, y: pd.merge(x, y, on='club_name', how='inner'), metric_dfs)


def fetch_agi_kagi(division: int, year: int) -> pd.DataFrame:
    """ Football LAB からAGIとKAGIを取得する """
    params = {'year': year, 'data': 'kagi'}
    url = FOOTBALL_LAB_URL.format(division=division)
    r = requests.get(url, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # 指標ランキングのテーブルを抽出（AGIとKAGIの2テーブル）
    tables = soup.find_all('table', class_='statsTbl')
    if not tables:
        return pd.DataFrame()

    agi_data = [{
        'club_name': tr.find('span', class_='dsktp').get_text(strip=True),
        'agi': float([td.get_text(strip=True) for td in tr.find_all('td')][AGI_COL])
    } for tr in tables[0].find_all('tr')[1:] if tr.find_all('td')]

    kagi_data = [{
        'club_name': tr.find('span', class_='dsktp').get_text(strip=True),
        'kagi': float([td.get_text(strip=True) for td in tr.find_all('td')][AGI_COL])
    } for tr in tables[1].find_all('tr')[1:] if tr.find_all('td')]

    # クラブ名を軸にAGI, KAGIをマージしたDataFrameを返却
    return pd.merge(pd.DataFrame(agi_data), pd.DataFrame(kagi_data), on='club_name', how='inner')


def normalize_columns(df: pd.DataFrame, cols: list, reverse_cols: set = set()) -> float:
    """ 0〜1のMin-Maxスケーリングを行う（invert=Trueで逆指標） """
    for col in cols:
        min_val, max_val = df[col].min(), df[col].max()
        norm_col = f'{col}_norm'
        if max_val == min_val:
            df[norm_col] = 0.5
        else:
            df[norm_col] = (df[col] - min_val) / (max_val - min_val)
            if col in reverse_cols:
                df[norm_col] = 1 - df[norm_col]

    return df


def compute_score(df: pd.DataFrame, weights: dict, label: str) -> pd.Series:
    norm_cols = [f'{col}_norm' for col in weights.keys()]
    weighted_sum = sum(df[norm_col] * weights[col]
                       for col, norm_col in zip(weights, norm_cols))

    return weighted_sum.round(3)


def calculate_play_style_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    各指標から攻撃スコアと守備スコアを計算する

    [攻撃スコア]
        * 平均ボール支配率（ball_rate）
        * シュート総数（shoot）
        * 得点総数（score）
        * チャンスクリエイト総数（chance_create）
        * AGI（agi）
    [守備スコア]
        * 平均ボール支配率（ball_rate）の逆指標
        * 被シュート総数（suffer_shoot）の逆指標
        * 失点総数（lost）の逆指標
        * ブロック総数（block_count）
        * KAGI（kagi）
    """
    all_cols = set(ATTACK_WEIGHTS) | set(DEFENSE_WEIGHTS)
    df = normalize_columns(df, list(all_cols), reverse_cols=REVERSE_INDICATORS)

    df['play_style_attack'] = compute_score(
        df, ATTACK_WEIGHTS, 'play_style_attack')
    df['play_style_defense'] = compute_score(
        df, DEFENSE_WEIGHTS, 'play_style_defense')

    return df[['club_name', 'play_style_attack', 'play_style_defense']]


def collect_play_style(year):
    combined = []
    for division in [1, 2, 3]:
        # JSTATSから指標を取得
        jstats_df = fetch_jstats_metric(division, year)
        # Football LAB から指標を取得
        flab_df = fetch_agi_kagi(division, year)
        # クラブ名を軸にjstats_dfとflab_dfをまとめる
        merged = pd.merge(jstats_df, flab_df, on='club_name', how='inner')
        combined.append(merged)

    # J1〜J3の集計結果を結合する
    full_df = pd.concat(combined, ignore_index=True)
    print(full_df)
    # 指標から攻撃スコア、守備スコアを計算する
    output_df = calculate_play_style_scores(full_df)

    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / 'play_style.csv'
    output_df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"Output {out_path}")
    print("Process finished.")
