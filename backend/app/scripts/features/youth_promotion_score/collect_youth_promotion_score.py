# 今シーズンの西暦を指定して実行する
# flak collect-youth 2025

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
BASE_URL = os.getenv('J_LEAGUE_URL') + \
    '/special/transfer/{year}/j{division}'


def fetch_youth_promotion_count(division: int, year: int) -> pd.DataFrame:
    """ Jリーグ公式の移籍情報からトップ昇格人数を取得する """
    url = BASE_URL.format(year=year, division=division)
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # クラブ毎の移籍情報を抽出
    articles = soup.find_all('article')
    if not articles:
        return pd.DataFrame()

    records = []
    for article in articles:
        club_name = article.select_one('h3').get_text(strip=True)
        # シーズン共通で持っているクラブの識別子
        club_identifier = article.select_one('span.embM').get('class')[1]
        # table.transferTableはINとOUTの2つあるが使うのはIN（1個目）のみ
        table_in = article.find('table', class_='transferTable')
        top_promotion_count = len([tr for tr in table_in.find_all('tr')[1:] if tr.find(
            'td', class_='etc').get_text(strip=True) == 'トップ昇格'])
        records.append({
            'club_name': club_name,
            'club_identifier': club_identifier,
            'top_promotion_count': top_promotion_count
        })

    return pd.DataFrame(records)


def collect_youth_promotion_score(current_year):
    # 今年+過去4シーズン分を取得
    target_years = list(range(int(current_year), int(current_year) - 5, -1))
    print(f'target_years: {target_years}')
    all_years_data = []
    for year in target_years:
        # シーズン毎のJ1〜J3全クラブのトップ昇格人数を取得する
        yearly_scores = []
        for division in [1, 2, 3]:
            df = fetch_youth_promotion_count(division, year)
            if df.empty:
                continue
            yearly_scores.append(
                df[['club_name', 'club_identifier', 'top_promotion_count']])
            time.sleep(1)  # スクレイピングの間隔を空けるため1秒待つ

        # 1シーズン毎のJ1〜J3全クラブのトップ昇格人数を1つのDataFrameにまとめall_years_dataに追加
        all_years_data.append(pd.concat(yearly_scores, ignore_index=True))

    # 今年のトップ昇格人数のDF（all_years_dataの先頭）を基準に過去シーズンのDFをclub_nameでLEFT結合していく
    # こうすることで、今シーズンJリーグに所属しているクラブのトップ昇格人数だけを抽出できる
    current_df = all_years_data[0].copy()
    for i, past_df in enumerate(all_years_data[1:], start=1):
        # 集計対象期間中に正式名が変更されたクラブもあるので、結合にはクラブの識別子を使い重複するクラブ名のカラムは除く
        current_df = current_df.merge(
            past_df[['club_identifier', 'top_promotion_count']],
            on='club_identifier', how='left', suffixes=('', f'_{i}')
        )

    # 各クラブ毎に5シーズン分のトップ昇格人数を合計する
    numeric_cols = current_df.select_dtypes(include='number')
    current_df['youth_promotion_score'] = numeric_cols.sum(axis=1).astype(int)
    print(current_df)
    # 結合に使ったクラブ識別子カラムの出力は不要なので削除
    current_df = current_df.drop(columns=['club_identifier'])

    print('')
    print('current_df')
    print(current_df)

    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / 'youth_promotion_score.csv'
    current_df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"Output {out_path}")
    print("Process finished.")
