from .extensions import db
from sqlalchemy import UniqueConstraint


class Club(db.Model):
    """ Jリーグクラブ情報のモデル
        id: 自動採番主キー
        name: クラブ名
        division: 所属ディビジョン（0=Jリーグ以外,1=J1, 2=J2, 3=J3）
        location: クラブ所在地
    """
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    division = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(120), nullable=False)


class Question(db.Model):
    """ ユーザに回答してもらう質問のモデル
        id: 自動採番主キー
        text: 質問文
        category: 質問のカテゴリ（地域、ファン・応援スタイル、歴史、チーム成績、サッカースタイルなど）
        TODO: カテゴリの内容を検討
        order: 表示順
        choices: 質問に紐づく選択肢リスト（Choiceモデル）
    """
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(255), nullable=False)
    category = db.Column(db.Integer, nullable=True)
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
