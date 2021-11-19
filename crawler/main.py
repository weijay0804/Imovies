"""

    爬取 IMdb 電影資料

"""

import time
from .model import PopularMovie, File
from typing import NoReturn

class Main():
    ''' 主程式 '''

    def __init__(self):
        self.file = File()
        self.popular = PopularMovie()
        

    def get_popular_movies(self, output_file_name : str,  item_limt : int = None) -> NoReturn:
        ''' 取得熱門電影資料，並輸出 json '''

        r = self.popular.get_imdb_datas(item_limit=item_limt)

        self.file.output_json_file(r,file_name=output_file_name)

    def get_popular_movie_details(self, movie_file_name : str, output_file_name : str) -> NoReturn:
        ''' 由 tmdb api 取得熱門電影詳細資料，並輸出 json '''

        datas = self.file.input_json_file(file_name=movie_file_name)
        r = []
        for data in datas:
            tmdb_id = data['tmdb_id']
            movie_detail = self.popular.get_movie_details(tmdb_id)
            r.append(movie_detail)
            print(tmdb_id)

            time.sleep(0.3)

        self.file.output_json_file(r,file_name=output_file_name)







