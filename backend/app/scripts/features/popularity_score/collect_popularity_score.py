# APのアクセス制限に引っかかるのを回避するため、J1、J2、J3で分けて実行する（1日1回ぐらいのペースが良さそう）
# flask collect-popularity j1
# flask collect-popularity j2
# flask collect-popularity j3

import pandas as pd
import time
import json
import instaloader
import os
from flask import current_app
from pathlib import Path
from googleapiclient.discovery import build
from apify_client import ApifyClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
APIFY_TOKEN = os.getenv('APIFY_TOKEN')
TWITTER_ACTOR = os.getenv('TWITTER_ACTOR')
START_J1_INDEX = 0
START_J2_INDEX = 20
START_J3_INDEX = 40


def get_youtube_subs(club_account_labels):
    """" クラブ毎の公式YouTubeチャンネルの登録者数を取得 """
    print('--- Start getting YouTube subscribers ---')
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    subscribers = {}
    for i, club_account_label in enumerate(club_account_labels):
        for club_name, account_labes in club_account_label.items():
            try:
                req = youtube.channels().list(
                    part='statistics', id=account_labes['youtube_channel_id'])
                res = req.execute()
                subscribers[club_name] = int(
                    res['items'][0]['statistics']['subscriberCount'])
            except Exception:
                subscribers[club_name] = None
        if (i + 1) % 20 == 0:
            print(f'{i + 1} clubs processed.')
    print('--- Finish getting YouTube subscribers ---')

    return subscribers


def get_instagram_twitter_followers(club_account_labels):
    """ クラブ毎の公式Instagramのフォロワー数を取得 """
    print('--- Start getting Instagram & Twitter followers ---')
    loader = instaloader.Instaloader()
    # Instagramはログインした方がアクセス制限が緩い（ユーザ名、パスワードは環境変数などに分ける）
    loader.login("mmsr_22", "helmut407")
    # TwitterはApifyのactorを利用
    client = ApifyClient(APIFY_TOKEN)
    instagram_followers = {}
    twitter_followers = {}
    for i, club_account_label in enumerate(club_account_labels):
        for club_name, account_labes in club_account_label.items():
            # Instagramのフォロワー数取得
            try:
                profile = instaloader.Profile.from_username(
                    loader.context, account_labes['instagram_user_name'])
                instagram_followers[club_name] = int(profile.followers)
            except Exception:
                instagram_followers[club_name] = None
            # Twitterのフォロワー数取得
            try:
                run_input = {
                    'from': account_labes['twitter_user_name'], 'maxItems': 1}
                run = client.actor(TWITTER_ACTOR).call(run_input=run_input)
                dataset_id = run.get('defaultDatasetId')
                followers = None
                if dataset_id:
                    for item in client.dataset(dataset_id).iterate_items():
                        author = item.get('author')
                        followers = author.get('followers')
                        if followers is not None:
                            break
                twitter_followers[club_name] = int(followers)
            except Exception:
                twitter_followers[club_name] = None
        time.sleep(60)  # Instagramのアクセス制限回避のため1分待機
        if (i + 1) % 5 == 0:
            print(f'{i + 1} clubs processed.')
    print('--- Finish getting Instagram & Twitter followers ---')

    return instagram_followers, twitter_followers


def collect_popularity_score(division):
    path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'settings' / 'jleague_clubs_sns.json'
    if not path.exists():
        raise FileNotFoundError(f'{path} not found')

    with open(path, 'r', encoding='utf-8') as f:
        club_account_labels = json.load(f)

    # 指定のdivisionのクラブだけ絞り込んで処理（Instagramのアクセス制限対策）
    if division.lower() == 'j1':
        club_account_labels = club_account_labels[START_J1_INDEX:START_J2_INDEX]
    elif division.lower() == 'j2':
        club_account_labels = club_account_labels[START_J2_INDEX:START_J3_INDEX]
    elif division.lower() == 'j3':
        club_account_labels = club_account_labels[START_J3_INDEX:]

    instagram_followers, twitter_followers = get_instagram_twitter_followers(
        club_account_labels)
    youtube_subscribers = get_youtube_subs(club_account_labels)

    data = []
    for club_account_label in club_account_labels:
        for club_name, account_labes in club_account_label.items():
            data.append({
                'club_name': club_name,
                'instagram_followers': instagram_followers.get(club_name),
                'twitter_followers': twitter_followers.get(club_name),
                'youtube_subscribers': youtube_subscribers.get(club_name),
            })

    df = pd.DataFrame(data)
    out_path = Path(current_app.root_path) / 'scripts' / \
        'features' / 'data' / f'popularity_raw_{division.lower()}.csv'
    df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'Output {out_path}')
    print('Process finished.')
