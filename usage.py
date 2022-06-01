from youtube_tools import MyYouTubeAPI

# set your api key and create instance of MyYouTubeAPI
API_KEY = 'Your api key'
myt = MyYouTubeAPI(API_KEY)

#
# let's make original functions!
#

# deal_playlist
def get_video_ids(myt, playlist_id):
    func = lambda response: [item['snippet']['resourceId']['videoId'] for item in response['items']]
    results = myt.deal_playlist(playlist_id, func, True, 'snippet')
    return results

# deal_videos
def get_titles(myt, video_ids):
    func = lambda response: [item['snippet']['title'] for item in response['items']]
    results = myt.deal_videos(video_ids, func, True, 'snippet')
    return results

# deal_channel
def get_statistics(myt, channel_ids):
    func = lambda response: [item['statistics'] for item in response['items']]
    results = myt.deal_channel(channel_ids, func, True, 'statistics')
    return results

def get_playlist_id_of_uploads(myt, channel_ids):
    func = lambda response: response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    results = myt.deal_channel(channel_ids, func, False, 'contentDetails')
    return results[0]