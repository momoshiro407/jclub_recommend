import click


def register_commands(app):
    @app.cli.command('seed-clubs')
    # --------------------------------------------------------
    # seedデータ投入・更新コマンド
    # --------------------------------------------------------
    def seed_clubs():
        """ J1〜J3全クラブをDBに投入
        """
        from .seeds.load import run_seed_clubs
        with app.app_context():
            run_seed_clubs()

    @app.cli.command('seed-questions')
    def seed_questions():
        """ 質問と選択肢をDBに投入
        """
        from .seeds.load import run_seed_questions
        with app.app_context():
            run_seed_questions()

    @app.cli.command('seed-weights')
    def seed_weights():
        """ 質問・選択肢の組と特徴量の重みのマッピング情報をDBに投入
        """
        from .seeds.load import run_seed_weights
        with app.app_context():
            run_seed_weights()

    @app.cli.command('seed-prefectures')
    def seed_prefectures():
        """ 都道府県データをDBに投入
        """
        from .seeds.load import run_seed_prefectures
        with app.app_context():
            run_seed_prefectures()

    @app.cli.command('update-club-features')
    def update_club_features():
        from .seeds.load import update_club_features
        with app.app_context():
            update_club_features()

    # --------------------------------------------------------
    # 特徴量集計用コマンド
    # --------------------------------------------------------
    @app.cli.command('collect-popularity')
    @click.argument('division')
    def exec_collect_popularity_score(division):
        from .scripts.features.popularity_score.collect_popularity_score import collect_popularity_score
        with app.app_context():
            collect_popularity_score(division=division)

    @app.cli.command('collect-attendance')
    @click.argument('year')
    def exec_collect_home_attendance(year):
        from .scripts.features.home_attendance.collect_home_attendance import collect_home_attendance
        with app.app_context():
            collect_home_attendance(year=year)

    @app.cli.command('collect-strength-long')
    @click.argument('year')
    def exec_collect_strength_long_term(year):
        from .scripts.features.strength.collect_strength_long_term import collect_strength_long_term
        with app.app_context():
            collect_strength_long_term(current_year=year)

    @app.cli.command('collect-strength-short')
    def exec_collect_strength_short_term():
        from .scripts.features.strength.collect_strength_short_term import collect_strength_short_term
        with app.app_context():
            collect_strength_short_term()

    @app.cli.command('collect-play-style')
    @click.argument('year')
    def exec_collect_play_style(year):
        from .scripts.features.play_style.collect_play_style import collect_play_style
        with app.app_context():
            collect_play_style(year=year)

    # --------------------------------------------------------
    # 特徴量DB登録用コマンド
    # --------------------------------------------------------
    @app.cli.command('update-popularity')
    def exec_update_popularity_score():
        from .scripts.features.popularity_score.update_popularity_score import update_popularity_score
        with app.app_context():
            update_popularity_score()

    @app.cli.command('update-attendance')
    def exec_update_home_attendance():
        from .scripts.features.home_attendance.update_home_attendance import update_home_attendance
        with app.app_context():
            update_home_attendance()

    @app.cli.command('update-availability')
    def exec_update_ticket_availability():
        from .scripts.features.ticket_availability.update_ticket_availability import update_ticket_availability
        with app.app_context():
            update_ticket_availability()

    @app.cli.command('update-strength')
    @click.argument('term')
    def exec_update_strength(term):
        from .scripts.features.strength.update_strength import update_strength
        with app.app_context():
            update_strength(term=term)

    @app.cli.command('update-play-style')
    def exec_update_play_style():
        from .scripts.features.play_style.update_play_style import update_play_style
        with app.app_context():
            update_play_style()
