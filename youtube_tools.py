import datetime
import json
import os
import time

import requests
from bs4 import BeautifulSoup as bs
from dateutil import tz
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

def convert_ISO8601(time='2018-09-23T13:43:00Z'):
    """Convert ISO8602 from yyyy-mm-ddTHH:MM:SSZ to datetime(%Y-%m-%d %H:%M)
    !!!ATTENTION!!!
        ISO8601 is shown in UCT. not jst.
    Args:
        time (str): str of time(yyyy-mm-ddTHH:MM:SSZ)

    Returns:
        datetime: datetime('%Y-%m-%d %H:%M)
    """
    JST = tz.gettz('Asia/Tokyo')
    UTC = tz.gettz('UTC')
    date_s = time[0:10]
    time_s = time[11:16]
    elem = date_s + ' ' + time_s
    date = datetime.datetime.strptime(elem, '%Y-%m-%d %H:%M')
    date_utc = date.replace(tzinfo=UTC)
    date_jst = date_utc.astimezone(JST)
    return date_jst.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M:%S')

#コンセプト
#情報取得を便利に
#加工はしない
class MyYouTubeAPI:
    def __init__(self, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, API_KEY):
        self.youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=API_KEY
        )

    #playlist idを指定したらとりあえずその情報を全て取得
    def get_playlist(self, playlist_id):
        playlist = []
        pagetoken = None
        while True:
            response = self.youtube.playlistItems().list(
                part = 'snippet',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken = pagetoken
                ).execute()
            print(response)
            time.sleep(1)

            playlist.extend(response['items'])

            #一度に読み込める回数が50件であるため、50件処理し終えるごとに次の50件を読み込む
            try:
                pagetoken = response['nextPageToken']
            except:
                break

        return playlist