# 今シーズンの西暦を指定して実行する
# flak collect-strength-long 2025

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np
from flask import current_app
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
J_LEAGUE_URL = os.getenv('J_LEAGUE_URL')
BASE_URL = J_LEAGUE_URL + '/standings/j{division}/'
# Jリーグ公式サイトの順位表に記載の試合結果アイコンの画像srcから結果を識別するための番号
# '/img/common/ico_match01.png'勝ち
# '/img/common/ico_match02.png'負け
# '/img/common/ico_match03.png'引き分け
WIN_ICON_NUMBER = '01'
LOSE_ICON_NUMBER = '02'
DRAW_ICON_NUMBER = '03'


def parse_match_icons(image_tags) -> list[int]:
    """ 試合結果アイコンのリストから勝点リストに変換する """
    points = []
    for img in image_tags:
        if WIN_ICON_NUMBER in img:
            points.append(3)
        elif LOSE_ICON_NUMBER in img:
            points.append(0)
        elif DRAW_ICON_NUMBER in img:
            points.append(1)
        else:
            continue

    return points


def normalize_points(points: list[int]) -> float:
    """ 直近5試合の勝点を正規化する（最大15点→1.0）"""
    # 実際の勝ち点合計 / 全勝の勝点（N*3）
    # 最大で直近5試合の結果を使う（1 ≦ N ≦ 5）
    max_point = len(points) * 3
    return float(round(np.sum(points) / max_point, 3))


def fetch_recent_match_results(division: int):
    """ Jリーグ公式サイトから順位表を取得し直近5試合の結果を抽出 """
    url = BASE_URL.format(division=division)
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    # 試合結果テーブル抽出
    table = soup.find('table', class_='scoreTable01')
    if not table:
        return []

    records = []
    # ヘッダー行を除いて各行のクラブ名と試合結果を取得する
    for tr in table.find_all('tr')[1:]:
        # 直近後試合の結果は勝敗のアイコン画像として含まれている
        result_images = [img['src'] for img in tr.find_all('img')]
        points = parse_match_icons(result_images)
        club_name = tr.select_one('span[class^="emb"]').get_text(strip=True)
        records.append({
            'club_name': club_name,
            'average_point': round(np.mean(points), 3),
            'strength_short_term': normalize_points(points)
        })

    return records


def collect_strength_short_term() -> None:
    results = [
        record
        for division in [1, 2, 3]
        for record in fetch_recent_match_results(division)
    ]

    df_out = pd.DataFrame(results)

    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'strength_short_term.csv'
    df_out.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Output {out_path}')
    print('Process finished.')
