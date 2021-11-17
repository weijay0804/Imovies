"""

    爬取 IMdb 電影資料

"""

import time
from model import PopularMovie, File
from typing import NoReturn
import json

class Main():
    ''' 主程式 '''

    def __init__(self):
        self.file = File()
        self.popular = PopularMovie()
        

    def get_popular_movies(self, item_limt : int = None) -> NoReturn:
        ''' 取得熱門電影資料，並輸出 json '''

        r = self.popular.get_imdb_datas(item_limit=item_limt)

        self.file.output_json_file(r, file_name='popular.json')

        return None

    def get_popular_movie_details(self, file_name : str) -> NoReturn:
        ''' 由 tmdb api 取得熱門電影詳細資料，並輸出 json '''

        datas = self.file.input_json_file(file_name=file_name)
        r = []
        for data in datas:
            tmdb_id = data['tmdb_id']
            movie_detail = self.popular.get_movie_details(tmdb_id)
            r.append(movie_detail)
            print(tmdb_id)

            time.sleep(1)

        self.file.output_json_file(r, file_name='popular_movie_details.json')

        return None

    def test(self):
        datas = self.file.input_json_file('popular_movie_details.json')
        for data in datas:
            tmdb_id = data['tmdb_id']
            url_tw = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key=d202f8126b1a52f67cc558860680dfa4&language=zh-TW'
            response = self.popular.get_url_datas(url_tw)
            j = json.loads(response.text)
        
            k = list(i['key'] for i in j.get('results'))

            if not k:
                url_en = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key=d202f8126b1a52f67cc558860680dfa4&language=en-US'
                response = self.popular.get_url_datas(url_en)
                j = json.loads(response.text)
                k = list(i['key'] for i in j.get('results'))

            print(k)
            print('-------------------------------')
            time.sleep(0.5)



if __name__ == '__main__':
    main = Main()
    main.get_popular_movie_details('popular.json')
    




