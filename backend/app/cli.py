def register_commands(app):
    @app.cli.command('seed-clubs')
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
