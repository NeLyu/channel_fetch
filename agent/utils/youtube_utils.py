import googleapiclient.discovery
import googleapiclient.errors
import sys
from pprint import pprint


def build_youtube_client(api_key):
    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)
    return youtube


def top_videos_by_keyword(youtube, key_word, max_results, order="relevance"):
    video_results = youtube.search().list(
        part="snippet",
        q=key_word,
        type="video",
        order=order,
        maxResults=max_results
        ).execute()
    
    video_titles = {}
    for item in video_results["items"]:
        video_titles[item["snippet"]["channelTitle"]] = [item["snippet"]["title"], 
                                                        item["id"]["videoId"]]

    return video_results, video_titles 


def channels_by_keyword(youtube, key_word, max_results):
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
        attributes = el["snippet"].keys()
        if "customUrl" in attributes:
            url = el["snippet"]["customUrl"]
            if url not in urls:
                selected.append(el)
                urls.append(url)
    return selected
    

def add_video_title_info(video_titles, sorted_channels):
    for el in sorted_channels:
        try:
            channel_title = el["snippet"]["title"]
            el["snippet"]["video_title"] = video_titles[channel_title][0]
            el["snippet"]["videoId"] = video_titles[channel_title][1]
        except KeyError:
            pass
    return sorted_channels


def get_video_titles(channel_id, youtube, max_results=15):

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"].strip()
        published = item["snippet"]["publishedAt"]
        videos.append({
            "title": title,
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published": published
        })

    return videos

def channel_info_by_name(name, youtube):
    request = youtube.search().list(
                    part="snippet",
                    q=name.strip(),
                    type="channel",
                    maxResults=2
                    )
    response = request.execute()
    channel_id = response["items"][0]["snippet"]["channelId"]

    request = youtube.channels().list(
        part="snippet",
        id=channel_id,
        maxResults=1,
    )

    response = request.execute()

    info = {name:
                {
                    "ID": channel_id,
                    "customUrl": response["items"][0]["snippet"]["customUrl"]
                }}

    return info