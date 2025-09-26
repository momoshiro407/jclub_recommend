from .extensions import db


class Club(db.Model):
    """ Jリーグクラブ情報のモデル
        id: 自動採番主キー
        name: クラブ名
        division: 所属ディビジョン（0=Jリーグ以外,1=J1, 2=J2, 3=J3）
        location: クラブ所在地
        image_url: クラブイメージ画像URL
        team_color: チームカラー（HEXカラーコード）
        website_url: 公式サイトURL
        main_stadium_name: メインのホームスタジアム名
        stadium_latitude: スタジアムの緯度
        stadium_longitude: スタジアムの経度
        description: クラブ説明文
        prefecture_id: 都道府県ID
        特徴量カラム: クラブの特徴を数値化したもの（推薦アルゴリズムで使用）
            - strength_long_term: 長期的な強さ
            - strength_short_term: 短期的な強さ
            - domestic_titles: 国内タイトル数
            - international_titles: 国際タイトル数
            - popularity_score: 人気度スコア
            - supporter_heat: サポーターの熱量
            - financial_power: 財政力
            - ticket_availability: チケットの取りやすさ
            - rivalry_intensity_preference: ライバル対戦の激しさ
            - play_style_attack: 攻撃的なサッカースタイルの度合い
            - play_style_defense: 守備的なサッカースタイルの度合い
            - play_style_youth: 若手育成重視の度合い
            - stadium_access: スタジアムのアクセスの良さ
            - stadium_capacity: スタジアムの収容人数
            - stadium_event_richness: スタジアム内イベントの多さ
            - attendance_average: 平均観客動員数
    """
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    division = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    team_color = db.Column(db.String(7), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)
    main_stadium_name = db.Column(db.String(120), nullable=True)
    stadium_latitude = db.Column(db.Float, nullable=True)
    stadium_longitude = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    prefecture_id = db.Column(
        db.Integer, db.ForeignKey('prefectures.id'), nullable=False, default=1, server_default="1")
    # ---- 特徴量カラム ----
    # Floatの場合は0.0〜1.0の正規化値を想定
    # Integerの場合は実数値を想定
    strength_long_term = db.Column(
        db.Float, nullable=False, default=0.5)
    strength_short_term = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    domestic_titles = db.Column(
        db.Integer, nullable=False, default=0, server_default="0")
    international_titles = db.Column(
        db.Integer, nullable=False, default=0, server_default="0")
    popularity_score = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    supporter_heat = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    financial_power = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    ticket_availability = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    rivalry_intensity_preference = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    play_style_attack = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    play_style_defense = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    play_style_youth = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    stadium_access = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    stadium_capacity = db.Column(
        db.Integer, nullable=False, default=15000, server_default="15000")
    stadium_event_richness = db.Column(
        db.Float, nullable=False, default=0.5, server_default="0.5")
    attendance_average = db.Column(
        db.Float, nullable=False, default=10000, server_default="10000")


class Question(db.Model):
    """ ユーザに回答してもらう質問のモデル
        id: 自動採番主キー
        text: 質問文
        order: 表示順
    """
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=True)

    # 質問削除時に選択肢も削除
    choices = db.relationship(
        'Choice',
        backref='question',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='Choice.order.asc()'
    )


class Choice(db.Model):
    """ 質問に対する選択肢のモデル
        id: 自動採番主キー
        question_id: 紐づく質問のID（外部キー）
        text: 選択肢文
        order: 表示順
    """
    __tablename__ = 'choices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id', ondelete='CASCADE'),
        nullable=False
    )
    text = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=True)


class QuestionChoiceWeight(db.Model):
    """ 質問・選択肢の組に対応する特徴量の重みのモデル
        id: 自動採番主キー
        question_id: 紐づく質問のID（外部キー）
        choice_id: 紐づく選択肢のID（外部キー）
        feature_name: 特徴量名
        weight: 重み
    """
    __tablename__ = 'question_choice_weights'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey(
        'questions.id', ondelete='CASCADE'), nullable=False)
    choice_id = db.Column(db.Integer, db.ForeignKey(
        'choices.id', ondelete='CASCADE'), nullable=False)
    feature_name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False, default=0.0)


class Prefecture(db.Model):
    """ 都道府県のモデル
        id: 自動採番主キー（1〜47）
        name: 都道府県名
    """
    __tablename__ = 'prefectures'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    clubs = db.relationship('Club', backref='prefecture', lazy=True)
