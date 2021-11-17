"""

    模組

"""

import json
import requests
import time
import os
from bs4 import BeautifulSoup
from typing import List, NoReturn
from dotenv import load_dotenv


class Movie():
    ''' 電影類別 '''

    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get('API_KEY')

    def get_url_datas(self, url : str) -> requests:
        ''' 獲得 url 的資料 '''

        response = requests.get(url)

        if response.status_code != 200:
            return f" 網路連線錯誤: {response.status_code} "
        
        return response

    def get_imdb_datas(self, url : str, item_limit : int = None) -> List[dict]:
        ''' 獲得 imdb 電影資料 '''

        response = self.get_url_datas(url)
        item_list = []

        soup = BeautifulSoup(response.text, 'html.parser')

        movie_items = soup.find('tbody', class_ = 'lister-list').find_all('tr', limit = item_limit)

        for movie_item in movie_items:
            title = movie_item.find('td', class_ = 'titleColumn').find('a').text
            imdb_id = movie_item.find('td', class_ = 'titleColumn').find('a').get('href').split('/')[2]
            tmdb_id = self.get_tmdb_id(imdb_id) if self.api_key else None
            item_list.append({
                'imdb_id' : imdb_id,
                'tmdb_id' : tmdb_id,
                'title' : title
            })
            print(title)
            time.sleep(0.5)
        
        return item_list


    def get_tmdb_id(self, imdb_id : str) -> int:
        ''' 根據 imdb id 獲得 tmdb 電影 id '''

        url = f'https://api.themoviedb.org/3/movie/{imdb_id}/external_ids?api_key={self.api_key}'
        response = self.get_url_datas(url)
        j = json.loads(response.text)

        tmdb_id = int(j.get('id')) if j.get('id') else None

        return tmdb_id

    def get_movie_details(self, tmdb_id : int) -> dict:
        ''' 由 tmdb api 獲得電影詳細資料 '''

        url_tw = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={self.api_key}&language=zh-TW'

        response_tw = self.get_url_datas(url_tw)

        j_tw = json.loads(response_tw.text)

        k = self.get_movie_video(tmdb_id)

        
        r = {
            'tmdb_id' : tmdb_id,
            'backdrop_path' : j_tw['backdrop_path'],
            'budget' : j_tw['budget'],
            'genres' : list( i['name'] for i in j_tw['genres'] ),
            'original_language' : j_tw['original_language'],
            'original_title' : j_tw['original_title'],
            'overview' : j_tw['overview'], 
            'poster_path' : j_tw['poster_path'],
            'video_key' : k,
            'release_date' : j_tw['release_date'],
            'runtime' : j_tw['runtime'],
            'status' : j_tw['status'],
            'title' :  j_tw['title'],
            'vote_average' : j_tw['vote_average'],
        }

        return r
    
    def get_movie_video(self, tmdb_id : int) -> List[str]:
        ''' 取得電影預告片 key '''
        
        url_tw = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={self.api_key}&language=zh-TW'

        response = self.get_url_datas(url_tw)
        j = json.loads(response.text)

        k = list(i.get('key') for i in j.get('results'))

        if not k:
            url_en = f'https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={self.api_key}&language=en-US'
            response = self.get_url_datas(url_en)
            j = json.loads(response.text)

            k = list(i.get('key') for i in j.get('results'))
        
        return k


            
class PopularMovie(Movie):
    ''' 熱門電影類別 '''

    def __init__(self):
        super().__init__()
        self.url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'

    def get_imdb_datas(self, item_limit: int = None,) -> List[tuple]:
        return super().get_imdb_datas(url = self.url, item_limit=item_limit)


class File():
    ''' 檔案處理類別 '''

    def __init__(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))

    
    def output_json_file(self, datas : List[dict], file_path : str = None, file_name : str = None) -> NoReturn:
        ''' 將資料儲存成 json 檔 '''
        
        f_path = file_path if file_path else self.basedir
        f_name = file_name if file_name else 'datas.json'
        file = os.path.join(f_path, f_name)

        if os.path.exists(file):
            print('錯誤!! 檔案已存在')
            return None

        if not file.endswith('.json'):
            print('錯誤!! 檔案副檔名必須是 .json')
            return None

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(datas, f, indent=4)


    def input_json_file(self, file_name : str, file_path : str = None) -> List[dict]:
        ''' 讀取 json 檔案並轉成 dict type '''

        f_path = file_path if file_path else self.basedir

        file = os.path.join(f_path, file_name)

        if not os.path.exists(file):
            print('錯誤!! 檔案不存在')

        if not file.endswith('.json'):
            print('錯誤!! 檔案副檔名必須是 .json')
            return None

        with open(file, 'r', encoding='utf-8') as f:
            r =   json.load(f)

        return r

        
        

