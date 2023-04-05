from googleapiclient.discovery import build
import os

def get_playlist_ids(channel_id):
    try:
        youtube = build ('youtube', 'v3', developerKey = os.getenv("api_key"))
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return playlist_id
    except Exception as e:
        print(e)
        return "INVALID"