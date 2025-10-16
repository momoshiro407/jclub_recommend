import os
from flask import current_app
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, select, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv(dotenv_path=Path(current_app.root_path) / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_no_show_rate(stadium_capacity):
    """ スタジアム収容上限に応じて欠席率を調整する """
    # 収容上限が大きいほど欠席率が高くなると仮定し、1.02〜1.12の範囲で調整する
    if stadium_capacity < 10000:
        return 1.03
    elif stadium_capacity < 20000:
        return 1.05
    elif stadium_capacity < 30000:
        return 1.08
    elif stadium_capacity < 40000:
        return 1.10
    else:
        return 1.13


def update_ticket_availability():
    engine = create_engine(DATABASE_URL)
    metadata = MetaData()
    clubs = Table('clubs', metadata, autoload_with=engine)

    with engine.begin() as conn:
        for division in [1, 2, 3]:
            # リーグ毎のクラブ情報を取得
            results = conn.execute(select(clubs).where(
                clubs.c.division == division)).fetchall()

            for club in results:
                stadium_capacity = club.stadium_capacity
                home_attendance = club.home_attendance
                club_name = club.name
                if not stadium_capacity or stadium_capacity <= 0 or not home_attendance:
                    continue
                # 欠席率（no_show_rate）を仮定してチケット販売枚数を概算する
                # 例えばno_show_rateが1.1の場合、「チケット販売枚数 = 入場者数 * 1.1」（チケット購入者の約10%が当日欠席と仮定）で算出
                sold_tickets = min(
                    stadium_capacity, home_attendance * get_no_show_rate(stadium_capacity))
                # 「チケット販売枚数 / 収容上限」でチケット販売率を算出し、1から引くことで「チケットの取りやすさ」を算出
                ticket_availability = 1 - (sold_tickets / stadium_capacity)
                ticket_availability = round(
                    max(0.001, min(1, ticket_availability)), 3)  # 0.001〜1に制限
                # DB更新
                query = text("""
                    UPDATE clubs
                    SET ticket_availability = :ticket_availability
                    WHERE normalize_alnum(name) = normalize_alnum(:club_name)
                """)
                conn.execute(
                    query, {
                        'ticket_availability': ticket_availability,
                        'club_name': club_name,
                    })
                print(f'[J{division}] {club_name}: {ticket_availability:.3f}')

    print(f'ticket_availability updated.')
