def register_commands(app):
    @app.cli.command('seed-clubs')
    def seed_clubs():
        """J1〜J3全クラブをDBに投入"""
        # run_seed は app context 必須
        from .seeds.load import run_seed
        with app.app_context():
            run_seed()
