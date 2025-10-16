# 入場者数を取得する対象の年を指定して実行する
# flak collect-attendance 2025

from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np
import os
from flask import current_app
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
J_DATA_SITE_URL = os.getenv('J_DATA_SITE_URL')
ATTENDANCE_COL = 6  # クラブ別入場者数の列番号


def scrape_home_attendance(team_id, division, year):
    """指定クラブのホーム試合入場者数リストを返す"""
    params = {
        'competition_year': year,
        'competition_frame': division,
        'teamIds': team_id,
        'teamType': 1,  # 0: 全て, 1: ホームのみ, 2: アウェイのみ
        'teamFlag': 0,
    }
    r = requests.get(J_DATA_SITE_URL, params=params)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')

    # Data Siteのテーブル構造を想定（class='tbl-data'）
    table = soup.find('table', class_='attendance-table')
    if not table:
        return []

    rows = table.find_all('tr', class_='bb')
    attendances = []
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all('td')]
        if not cols:
            continue
        # 入場者数の列を確認
        att_str = cols[ATTENDANCE_COL]
        if att_str:
            try:
                att = int(att_str.replace(',', ''))
                attendances.append(att)
            except ValueError:
                continue

    return attendances


def collect_home_attendance(year):
    # JleaguDataSite仕様のクラブ名とteam_idsの対応関係を記載したCSVを読み込む
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'settings' / 'jleague_team_ids.csv'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    # CSV読み込み（1行目コメント、2行目ヘッダー）
    teams = pd.read_csv(path, comment='#')
    # クラブ情報をリスト化
    club_list = teams[['club_name', 'division',
                       'team_ids']].to_dict(orient='records')

    results = []
    # J1のクラブから順に処理
    for division in [1, 2, 3]:
        target_clubs = [c for c in club_list if c['division'] == division]
        for i, club in enumerate(target_clubs):
            club_name = club['club_name']
            team_ids = club['team_ids']

            attendances = scrape_home_attendance(team_ids, division, year)
            if attendances:
                # 特徴量として使うのは平均値・中央値のいずれかだが一応両方計算しておく
                avg_att = int(round(np.mean(attendances)))
                med_att = int(round(np.median(attendances)))
            else:
                avg_att, med_att = None, None

            results.append({
                'club_name': club_name,
                'division': division,
                'average_attendance': avg_att,
                'median_attendance': med_att
            })
            if i + 1 == 20:
                print(f'All J{division} club\'s attendances are calculated.')

    df_out = pd.DataFrame(results)
    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'home_attendance_raw.csv'
    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Output {out_path}')
    print('Process finished.')
