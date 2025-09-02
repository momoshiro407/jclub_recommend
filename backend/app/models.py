from .extensions import db


class Club(db.Model):
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    division = db.Column(db.Integer, nullable=False)  # 1=J1, 2=J2, 3=J3
    location = db.Column(db.String(120), nullable=False)
