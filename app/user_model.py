'''

    使用者資料庫模型

'''

from app import db
from typing import NoReturn
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    ''' user 資料表 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(128), unique = True, index = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))

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
