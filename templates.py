# コンパクトに書く必要がなければ以下を改変したほうがわかりやすい
import time

from googleapiclient.discovery import build

API_KEY = 'Your api key'

youtube = build(
    'youtube',
    'v3',
    developerKey=API_KEY
)

def template_under50(youtube, id):
    # 関数ごとに自由に設定
    response = youtube.channels().list(
        part = 'snippet',
        id = id,
        maxResults = 50,
    ).execute()

    # 処理を記述

    return

def template_over50(youtube, id):
    pagetoken = None
    while True:
        # 関数ごとに自由に設定
        response = youtube.channels().list(
            part = 'snippet',
            id = id,
            maxResults = 50,
            pageToken = pagetoken
        ).execute()
        time.sleep(1)

        # 処理を記述

        #一度に読み込める回数が50件であるため、50件処理し終えるごとに次の50件を読み込む
        try:
            pagetoken = response['nextPageToken']
        except:
            break
    return