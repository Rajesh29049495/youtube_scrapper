from googleapiclient.discovery import build
import os


##function to get comment items
def get_comment_items(youtube, video_id, nextPageToken=None):
    items = []
    response_comments = youtube.commentThreads().list(
        part='snippet, replies',
        videoId=video_id,
        pageToken=nextPageToken
    ).execute()
    items.extend(response_comments['items'])

    if 'nextPageToken' in response_comments:
        response_comments1 = youtube.commentThreads().list(
            part='snippet, replies',
            videoId=video_id,
            pageToken=response_comments['nextPageToken']
        ).execute()
        items.extend(response_comments1['items'])
    else:
        return items
    return items


def get_comments(video_id, video_title):
    try:
        youtube = build('youtube', 'v3', developerKey=os.getenv("api_key"))
        response_comments = get_comment_items(youtube, video_id)
        commentCount = len(response_comments)
        comments = {
            'videoId': video_id,
            'title': video_title,
            'commentCount': commentCount,
            'comments': []
        }
        for response in response_comments:
            totalReplyCount = response['snippet']['totalReplyCount']
            if totalReplyCount != 0:
                if 'replies' in response:
                    replies = []
                    for i in response['replies']['comments']:
                        iter = dict(authorname=i['snippet']['authorDisplayName'],
                                    comment=i['snippet']['textOriginal'],
                                    likecount=i['snippet']['likeCount'],
                                    publishedAt=i['snippet']['publishedAt'])
                        replies.append(iter)
                else:
                    replies = []
            else:
                replies = []
            comments['comments'].append(
                {
                    "author_Name": response['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    "comment": response['snippet']['topLevelComment']['snippet']['textOriginal'],
                    "publishedAt": response['snippet']['topLevelComment']['snippet']['publishedAt'],
                    "likeCount": response['snippet']['topLevelComment']['snippet']['likeCount'],
                    "replies": replies
                })
    except Exception as e:
        print(e)
        comments = {
            'videoId': video_id,
            'title': video_title,
            'commentCount': 0,
            'comments': []
        }
    return comments


