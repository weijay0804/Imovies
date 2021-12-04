'''

    使用者資料庫模型

'''

import hashlib
from typing import NoReturn
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager, db

user_movies = db.Table(
    'user_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
)

user_watched_movies = db.Table(
    'user_watched_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'))
)


class Comments(db.Model):
    ''' 使用者評論表 '''

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow, index = True)
    like = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

class Users(db.Model, UserMixin):
    ''' user 資料表 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(128), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    about_me = db.Column(db.Text)
    location = db.Column(db.String(64))
    favorite_movie_genres = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    movies = db.relationship('Movies', secondary = user_movies, backref = db.backref('users', lazy = 'dynamic'), lazy = 'dynamic')
    watched_movies = db.relationship('Movies', secondary = user_watched_movies, backref = db.backref('watched_users', lazy = 'dynamic'), lazy = 'dynamic')
    comments = db.relationship('Comments', backref = 'user', lazy = 'dynamic')


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if self.username is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()


    @property
    def password(self) -> NoReturn:
        ''' 讓外部無法讀取 pssword 屬性 '''
        raise AttributeError('Password is not a readablb attribute.')

    @password.setter
    def password(self, password : str) -> NoReturn:
        ''' 將密碼雜湊後儲存至資料庫 '''

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password : str) -> bool:
        ''' 檢查使用者密碼是否正確 '''

        return check_password_hash(self.password_hash, password)

    def ping(self) -> None:
        ''' 更新使用者登入時間 '''

        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self) -> str:
        ''' 根據使用者 username 產生 md5 hash 值'''

        hash = hashlib.md5(self.username.lower().encode('utf-8')).hexdigest()

        return hash
        
    def gravatar(self, size : int = 100, default : str = 'identicon', rating : str = 'g') -> str:
        ''' 生成使用者頭相 url '''

        url = 'https://www.gravatar.com/avatar'

        hash = self.avatar_hash or self.gravatar_hash()
        

        return f'{url}/{hash}?s={size}&d={default}&r={rating}'

@login_manager.user_loader
def load_user(user_id):
    ''' 載入使用者 '''
    return Users.query.get(int(user_id))