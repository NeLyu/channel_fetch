import googleapiclient.discovery
import googleapiclient.errors
import sys
from pprint import pprint

def build_youtube_client(api_key):
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
    return youtube


def top_videos_by_keyword(youtube, key_word, max_results=10):
    video_results = youtube.search().list(
        part="snippet",
        q=key_word,
        type="video",
        order="viewCount",
        maxResults=max_results
        ).execute()
    
    video_titles = {}
    for item in video_results["items"]:
        video_titles[item["snippet"]["channelTitle"]] = item["snippet"]["title"]

    return video_results, video_titles 


def channels_by_keyword(youtube, key_word, max_results=10):
    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=key_word
    )
    response = request.execute()
    return response


def get_channel_name(response):
    channel_name = response["items"][0]["snippet"]["channelTitle"]
    return channel_name


def get_channel_info(channel_id, youtube):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    channel_info = request.execute()
    return channel_info


def get_channel_ids(video_results):
    all_ids = [item['snippet']['channelId'] for item in video_results['items']]
    unique_ids = list(set(all_ids))
    return unique_ids


def sort_channels(channels):
    sorted_channels = sorted(
        channels["items"],
        key=lambda c: int(c["statistics"].get("subscriberCount", 0)),
        reverse=True
        )
    return sorted_channels


def scrape_channels_through_api(youtube, query, n):
    top_videos, video_titles = top_videos_by_keyword(youtube, query, n)
    channel_ids = get_channel_ids(top_videos)
    channels_response = get_channel_info(channel_ids, youtube)
    return channels_response, video_titles


def sort_channels(channels):
    sorted_channels = sorted(
        channels["items"],
        key=lambda c: int(c["statistics"].get("subscriberCount", 0)),
        reverse=True
        )
    return sorted_channels

def remove_duplicate_channels(sorted_channels):
    urls = []
    selected = []
    for el in sorted_channels:
        url = el["snippet"]["customUrl"]
        if url not in urls:
            selected.append(el)
            urls.append(url)
    return selected

def add_video_title_info(video_titles, sorted_channels):
    # print(video_titles.keys())
    for el in sorted_channels:
        channel_title = el["snippet"]["title"]
        el["snippet"]["video_title"] = video_titles[channel_title]

    return sorted_channels