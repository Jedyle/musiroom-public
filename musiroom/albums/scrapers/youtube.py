from django.conf import settings
from youtube_api import YouTubeDataAPI


def fetch_youtube_link(album):
    yt = YouTubeDataAPI(settings.YOUTUBE_API_KEY)
    search_string = f"{album.artists.first().name} {album.title}"
    res = yt.search(search_string, max_results=1)
    return f"https://youtube.com/watch?v={res[0]['video_id']}"
