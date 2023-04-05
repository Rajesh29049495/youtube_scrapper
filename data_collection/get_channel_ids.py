import requests
from bs4 import BeautifulSoup

def get_channel_ids(youtube_url):
    try:
        response = requests.get(youtube_url)
    except Exception as e:
        print(e)
        return 'INVALID'                                      ##this use of "INVALID" text is just to giev the clear idea to teh caller of teh function that something went wrong

    if response.ok== True:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        youtube_url = youtube_url.replace("user", "c")
        response = requests.get(youtube_url)
        soup = BeautifulSoup(response.text, 'html.parser')
    
    channel_id = soup.find('link', rel="canonical")["href"].split('/')[-1]
    return channel_id