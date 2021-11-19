'''

    app 資料庫模型

'''

from app import db
from datetime import datetime
from crawler.model import File
from config import Config
from typing import NoReturn
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Movies(db.Model):
    ''' 電影資料 '''

    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key = True)
    tmdb_id = db.Column(db.Integer, unique = True, index = True)
    imdb_id = db.Column(db.String(15), unique = True)
    backdrop_path = db.Column(db.String(40))
    budget = db.Column(db.Integer)
    genres = db.Column(db.Text)
    original_language = db.Column(db.String(10))
    original_title = db.Column(db.Text)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.String(40))
    video_key = db.Column(db.Text)
    release_date = db.Column(db.Date)
    runtime = db.Column(db.Integer)
    status = db.Column(db.String(30))
    title = db.Column(db.Text)
    vote_average = db.Column(db.Float)
    insert_datetime = db.Column(db.DateTime, default = datetime.utcnow)

    # TODO 重構程式碼
    @staticmethod
    def insert_datas():
        ''' 將 json 資料寫入資料庫 '''

        # 獲得資料庫中的資料，便於之後比對
        movies = Movies.query.all()
        tmdb_id_set = set(i.tmdb_id for i in movies)

        # 開啟 json 檔案，檔案必須位於根目錄
        file_name = os.path.join(Config.BASEDIR, 'toprank_movies.json')
        f = File()
        datas = f.input_json_file(file_name)

        # insert 資料到資料庫
        for data in datas:
            # 如果資料已經存在資料庫就跳過
            if data['tmdb_id'] in tmdb_id_set:
                continue
            
            data['genres'] = ','.join(data['genres'])
            data['video_key'] = ','.join(data['video_key'])

            try:
                data['release_date'] = datetime.strptime(data['release_date'], "%Y-%m-%d")
            except:
                data['release_date'] = None
            
            m = Movies(**data)

            db.session.add(m)
        db.session.commit()


class PopularMovies(db.Model):
    ''' 熱門電影資料 '''

    __tablename__ = 'popularmovies'

    id = db.Column(db.Integer, primary_key = True)
    tmdb_id = db.Column(db.Integer, unique = True, index = True)
    imdb_id = db.Column(db.String(15), unique = True)
    title = db.Column(db.Text)
    insert_datetime = db.Column(db.DateTime, default = datetime.utcnow)

    # TODO 重構程式碼
    @staticmethod
    def insert_datas() -> NoReturn:
        ''' 將 json 資料寫入資料庫 '''

        # 獲得資料庫中的資料，便於之後比對
        movies = PopularMovies.query.all()
        tmdb_id_set = set(i.tmdb_id for i in movies)

        # 開啟 json 檔案，檔案必須位於根目錄
        file_name = os.path.join(Config.BASEDIR, 'popular.json')
        f = File()
        datas = f.input_json_file(file_name)

        # insert 資料到資料庫
        for data in datas:
            # 如果資料已經存在資料庫就跳過
            if data['tmdb_id'] in tmdb_id_set:
                continue

            m = PopularMovies(**data)

            db.session.add(m)
        db.session.commit()


class TopRankMoives(db.Model):
    ''' 熱門電影資料 '''

    __tablename__ = 'toprankmovies'

    id = db.Column(db.Integer, primary_key = True)
    tmdb_id = db.Column(db.Integer, unique = True, index = True)
    imdb_id = db.Column(db.String(15), unique = True)
    title = db.Column(db.Text)
    insert_datetime = db.Column(db.DateTime, default = datetime.utcnow)

    # TODO 重構程式碼
    @staticmethod
    def insert_datas() -> NoReturn:
        ''' 將 json 資料寫入資料庫 '''

        # 獲得資料庫中的資料，便於之後比對
        movies = TopRankMoives.query.all()
        tmdb_id_set = set(i.tmdb_id for i in movies)

        # 開啟 json 檔案，檔案必須位於根目錄
        file_name = os.path.join(Config.BASEDIR, 'toprank.json')
        f = File()
        datas = f.input_json_file(file_name)

        # insert 資料到資料庫
        for data in datas:
            # 如果資料已經存在資料庫就跳過
            if data['tmdb_id'] in tmdb_id_set:
                continue

            m = TopRankMoives(**data)

            db.session.add(m)
        db.session.commit()
        

    