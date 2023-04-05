from googleapiclient.discovery import build
import os
import pandas as pd


def get_video_details(playlist_id, maxResults=5):
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv("api_key"))
        response_playlist = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=maxResults
        ).execute()
        data = {
            'thumbnail': [],
            'title': [],
            'publishedAt': [],
            'videoLink': [],
            'video_id': []
        }

        channel_title = ""

        for item in response_playlist["items"]:
            snippet = item['snippet']
            data['thumbnail'].append(snippet['thumbnails']['default']['url'])
            data['title'].append(snippet['title'])
            data['publishedAt'].append(snippet['publishedAt'])

            video_id = snippet['resourceId']['videoId']
            video_link = f"https://www.youtube.com/watch?v={video_id}"

            data['video_id'].append(video_id)
            data['videoLink'].append(video_link)

            channel_title = snippet["channelTitle"]

        data1 = {
            'view_count': [],
            'like_count': [],
            'comment_count': []
        }

        for video_id in data['video_id']:
            response_video = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()
            data1['view_count'].append(response_video['items'][0]['statistics']['viewCount'])
            data1['like_count'].append(response_video['items'][0]['statistics']['likeCount'])
            data1['comment_count'].append(response_video['items'][0]['statistics']['commentCount'])

        data = {**data, **data1}

        video_data = pd.DataFrame(data)
        video_data["comments"] = video_data["video_id"] + "#SPLIT#" + video_data["comment_count"].astype(str)  ##"#SPLIT#" is a string that is used to separate the values of the two columns in the new column being formed
        video_data["video_title"] = video_data["title"] + "#SPLIT#" + video_data["videoLink"].astype(str)
        video_data["download_link"] = video_data["video_id"]
        return video_data, channel_title
    except Exception as e:
        print(e)
        return None, None