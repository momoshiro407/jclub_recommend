# 今シーズンの西暦を指定して実行する
# flak collect-strength-long 2025

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from flask import current_app
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
FOOTBALL_LAB_URL = os.getenv('FOOTBALL_LAB_URL')
BASE_URL = FOOTBALL_LAB_URL + '/team_ranking/j{division}'
STANDING_COL = 0  # 順位表の順位の列番号
CLUB_NAME_COL = 2  # 順位表のクラブ名の列番号

# リーグ別の長期的強さスコア計算用パラメータ（base, beta）
DIV_PARAMS = {
    1: (0.70, 0.30),
    2: (0.40, 0.30),
    3: (0.20, 0.30),
}


def fetch_standings(division: int, year: int) -> pd.DataFrame:
    """ Football-Labからリーグ別・シーズン別の順位表を取得 """
    url = BASE_URL.format(division=division)
    r = requests.get(url, params={'year': year})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    # 順位テーブル抽出
    table = soup.find('table', id='standing')
    if not table:
        return pd.DataFrame()

    records = []
    # ヘッダー行を除いて各行のクラブ名と順位を取得する
    for tr in table.find_all('tr')[1:]:
        cols = [td.get_text(strip=True) for td in tr.find_all('td')]
        if not cols:
            continue
        standing = int(cols[STANDING_COL])
        club_name = tr.find('span', class_='dsktp').get_text(strip=True)
        club_name_short = tr.find('span', class_='sp').get_text(strip=True)
        records.append({
            'club_name': club_name,
            'club_name_short': club_name_short,
            'standing': standing,
            'division': division
        })

    return pd.DataFrame(records)


def calc_strength_score(standing: int, total_clubs: int, division: int) -> float:
    """ 順位から同シーズン内の強さを示すスコアを計算 """
    base, beta = DIV_PARAMS[division]
    # 1位が1、最下位が0になるように正規化する
    normalized = 1 - (standing - 1) / (total_clubs - 1)
    # 正規化したスコアに所属リーグ毎のスコアの底上げ分baseを加算する
    # bataは同一リーグ内で順位による変動幅を制御する係数で、上位の最下位と下位の1位との接続が滑らかになるように調整する

    return round(base + beta * normalized, 3)


def collect_strength_long_term(current_year) -> None:
    # 今年+過去4シーズン分を取得
    target_years = list(range(int(current_year), int(current_year) - 5, -1))
    all_years_data = []
    for year in target_years:
        # シーズン毎のJ1〜J3全クラブの強さスコアを格納するリスト
        yearly_scores = []
        # J1, J2, J3それぞれ順位表から計算した各クラブのスコアを取得
        for division in [1, 2, 3]:
            df = fetch_standings(division, year)
            if df.empty:
                continue
            df['strength_score'] = df['standing'].apply(
                lambda s: calc_strength_score(s, len(df), division)
            )
            yearly_scores.append(
                df[['club_name', 'club_name_short', 'strength_score']])
            time.sleep(1)  # スクレイピングの間隔を空けるため1秒待つ

        # 1シーズン毎のJ1〜J3全クラブの強さスコアを1つのDataFrameにまとめscore_dfsに追加
        all_years_data.append(pd.concat(yearly_scores, ignore_index=True))

    # 今年のスコアDF（score_dfsの先頭）を基準に過去シーズンのスコアDFをclub_nameでLEFT結合していく
    # こうすることで、今シーズンJリーグに所属しているクラブのスコアだけを抽出できる
    current_df = all_years_data[0].copy()
    for i, past_df in enumerate(all_years_data[1:], start=1):
        # 結合にはクラブ略称のみ使い、重複するクラブ名のカラムは除く
        current_df = current_df.merge(
            past_df[['club_name_short', 'strength_score']],
            on='club_name_short', how='left', suffixes=('', f'_{i}')
        )

    # 各クラブ毎に5シーズン分のスコアを平均して長期的な強さのスコアを計算
    numeric_cols = current_df.select_dtypes(include='number')
    current_df['strength_long_term'] = numeric_cols.mean(axis=1).round(3)
    print(current_df)
    # 結合に使ったクラブ略称カラムの出力は不要なので削除
    current_df = current_df.drop(columns=['club_name_short'])

    print('')
    print('current_df')
    print(current_df)

    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'strength_long_term.csv'
    current_df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Output {out_path}')
    print('Process finished.')
