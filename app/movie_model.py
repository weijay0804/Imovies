'''

    app 電影資料庫模型

'''

import os
from app import db
from datetime import datetime
from typing import NoReturn
from crawler.model import File
from config import Config



class Generes():
    # 還有一個 紀錄 類別，因為沒有電影是記錄類別，所以沒放
    generes_en = {
        '動作' : 'action',
        '犯罪' : 'crime',
        '戰爭' : 'war',
        '奇幻' : 'fantasy',
        '驚悚' : 'thriller',
        '動畫' : 'fantasy',
        '歷史' : 'history',
        '西部' : 'western',
        '冒險' : 'adventure',
        '科幻' : 'science-fiction',
        '恐怖' : 'crime',
        '電視電影' : 'TV-movie',
        '劇情' : 'drama',
        '懸疑' : 'mystery',
        '音樂' : 'music',
        '家庭' : 'family',
        '愛情' : 'romance',
        '喜劇' : 'comedy',
    }

    # 還有一個 紀錄 類別，因為沒有電影是記錄類別，所以沒放
    genres_set = [
        '冒險',
        '劇情',
        '動作',
        '科幻',
        '奇幻',
        '戰爭',
        '犯罪',
        '懸疑', 
        '驚悚',
        '恐怖',
        '西部',
        '歷史',
        '紀錄',
        '喜劇', 
        '家庭', 
        '動畫', 
        '電視電影', 
        '愛情', 
        '音樂',
        ]

class BaseMovie():
    ''' 基本 movie 資料庫類別 '''

    @classmethod
    def insert(cls, file : str) -> NoReturn:
        ''' 將 json 資料寫入資料庫 '''

        # 獲得資料庫中的資料，便於之後比對
        movies = cls.query.all()
        tmdb_id_set = set(i.tmdb_id for i in movies)

        # 開啟 json 檔案，檔案必須位於根目錄
        file_name = os.path.join(Config.BASEDIR, file)
        f = File()
        datas = f.input_json_file(file_name)

        # insert 資料到資料庫
        for data in datas:
            # 如果資料已經存在資料庫就跳過
            if data['tmdb_id'] in tmdb_id_set:
                continue

            m = cls(**data)

            db.session.add(m)
        db.session.commit()
        print('Done!')

    @classmethod
    def update(cls, file : str) -> NoReturn:
        ''' 更新資料庫中的資料 '''

        f = File()
        datas = f.input_json_file(file_name=file, file_path=Config.BASEDIR)

        for data in datas:
            tmdb_id = data['tmdb_id']
            
            data['insert_datetime'] = datetime.utcnow()

            cls.query.filter(cls.tmdb_id == tmdb_id).update(data)

        db.session.commit()
        print('Done! ')


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
    insert_datetime = db.Column(db.DateTime(), default = datetime.utcnow)

    comments = db.relationship('Comments', backref = 'movie', lazy = 'dynamic')

    @staticmethod
    def insert(file : str):
        ''' 將 json 資料寫入資料庫 '''

        # 獲得資料庫中的資料，便於之後比對
        movies = Movies.query.all()
        tmdb_id_set = set(i.tmdb_id for i in movies)

        # 開啟 json 檔案，檔案必須位於根目錄
        file_name = os.path.join(Config.BASEDIR, file)
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
        print('Done!')

    @staticmethod
    def update(file : str) -> NoReturn:
        ''' 更新資料庫中的資料 '''
        
        f = File()
        datas = f.input_json_file(file_path=Config.BASEDIR, file_name=file)

        for data in datas:
            tmdb_id = data['tmdb_id']
            data['genres'] = ','.join(data['genres'])
            data['video_key'] = ','.join(data['video_key'])
            try:
                data['release_date'] = datetime.strptime(data['release_date'], "%Y-%m-%d")
            except:
                data['release_date'] = None
            data['insert_datetime'] = datetime.utcnow()
            
            Movies.query.filter(Movies.tmdb_id == tmdb_id).update(data)
        
        db.session.commit()
        print('Done! ')

    @staticmethod
    def get_movie_genres():
        movies = Movies.query.all()
        movie_type = set(y 
            for movie in movies
            for y in movie.genres.split(',')
            )
        print(movie_type)





class PopularMovies(db.Model, BaseMovie):
    ''' 熱門電影資料 '''

    __tablename__ = 'popularmovies'

    id = db.Column(db.Integer, primary_key = True)
    tmdb_id = db.Column(db.Integer, unique = True, index = True)
    imdb_id = db.Column(db.String(15), unique = True)
    title = db.Column(db.Text)
    insert_datetime = db.Column(db.DateTime(), default = datetime.utcnow)

    @classmethod
    def insert(cls, file: str) -> NoReturn:
        return super().insert(file)

    @classmethod
    def update(cls, file: str) -> NoReturn:
        return super().update(file)

        


class TopRankMoives(db.Model, BaseMovie):
    ''' 熱門電影資料 '''

    __tablename__ = 'toprankmovies'

    id = db.Column(db.Integer, primary_key = True)
    tmdb_id = db.Column(db.Integer, unique = True, index = True)
    imdb_id = db.Column(db.String(15), unique = True)
    title = db.Column(db.Text)
    insert_datetime = db.Column(db.DateTime(), default = datetime.utcnow)

    @classmethod
    def insert(cls, file: str) -> NoReturn:
        return super().insert(file)

    @classmethod
    def update(cls, file: str) -> NoReturn:
        return super().update(file)
        
        

    