import datetime
import time

import requests
from bs4 import BeautifulSoup as bs
from googleapiclient.discovery import build
from yt_dlp import YoutubeDL


def get_thumbnail_url(video_id, size=4):
    sizes = ['', 'mq', 'hq', 'sd', 'maxres']
    url = f'https://i.ytimg.com/vi/{video_id}/{sizes[size]}default.jpg'
    if requests.get(url):
        return url
    else:
        print(f'size {size} does not exits')
        return get_largest_thumbnail_url

def get_largest_thumbnail_url(video_id):
    sizes = ['', 'mq', 'hq', 'sd', 'maxres']
    for size in reversed(sizes):
        url = f'https://i.ytimg.com/vi/{video_id}/{size}default.jpg'
        if requests.get(url):
            return url
        else:
            continue

def get_playlist_id(playlist_url):
    return playlist_url.split('=',1)[-1]

def get_playlist_title(playlist_id):
    url = f'https://www.youtube.com/playlist?list={playlist_id}'
    response = requests.get(url)
    soup = bs(response.content, 'html.parser')
    return soup.select_one('body > title').text.replace(' - YouTube','')

def get_video_ids_from_playlist(playlist_id):
    url = f'https://www.youtube.com/playlist?list={playlist_id}'
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            meta = ydl.extract_info(url, download=False)
        except:
            print("\nerror")
            exit(1)
    video_ids = []
    for items in meta["entries"]:
        video_ids.append(items["id"])
    return video_ids

def convert_ISO8601(iso8601='2018-09-23T13:43:00Z'):
    """Convert ISO8602 to datetime
    !!!ATTENTION!!!
        ISO8601 is shown in UCT. not jst.
    Args:
        iso8601 (str): str of time(yyyy-mm-ddTHH:MM:SSZ)

    Returns:
        datetime (datetime): aware jst datetime(yyyy-mm-dd HH:MM:SS+09:00)
    """
    t_native = datetime.datetime.strptime(iso8601, '%Y-%m-%dT%H:%M:%SZ')
    t_aware = t_native.replace(tzinfo=datetime.timezone.utc)
    JST = datetime.timezone(datetime.timedelta(hours=9))
    t_aware_jst = t_aware.astimezone(JST)
    return t_aware_jst

#コンセプト
#情報取得を便利に
#加工はしない
class MyYouTubeAPI:
    def __init__(self, API_KEY):
        self.youtube = build(
            'youtube',
            'v3',
            developerKey=API_KEY
        )

    # 50件以上まとめての処理をパーツ化
    def base(self, response_formula, func, extend=False):
        results = []
        pagetoken = None

        while True:
            response = response_formula(pagetoken).execute()
            time.sleep(1)

            result = func(response)
            if result is not None:
                if extend:
                    results.extend(result)
                else:
                    results.append(result)

            #一度に読み込める回数が50件であるため、50件処理し終えるごとに次の50件を読み込む
            try:
                pagetoken = response['nextPageToken']
            except:
                break

        if results != []: return results

    # playlist, video, channelなどを扱う土台
    def deal_playlist(self, playlist_id, func, extend=False, part='snippet'):
        def response_formula(pagetoken):
            return self.youtube.playlistItems().list(
            part = part,
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = pagetoken
            )
        results = self.base(response_formula, func, extend)
        return results

    def deal_videos(self, video_ids, func, extend=False, part='snippet'):
        def response_formula(pagetoken):
            return self.youtube.videos().list(
                part = part,
                id = ','.join(video_ids),
                maxResults = 50,
                pageToken = pagetoken
                )
        results = self.base(response_formula, func, extend)
        return results

    def deal_channel(self, channel_ids, func, extend=False, part='statistics'):
        def response_formula(pagetoken):
            return self.youtube.channels().list(
                part = part,
                id = ','.join(channel_ids),
                maxResults = 50,
                pageToken = pagetoken
                )
        results = self.base(response_formula, func, extend)
        return results