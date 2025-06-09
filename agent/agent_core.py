from agent.utils.prompt_loader import load_prompt_template
import agent.utils.youtube_utils as yt
from openai import OpenAI
from dotenv import load_dotenv
import os, json

def remove_openai_additions(openai_output):
    openai_output = openai_output.replace("```json\n", "")
    openai_output = openai_output.replace("```", "")
    return openai_output

def extract_channels(openai_output, youtube, n):
    openai_output = json.loads(remove_openai_additions(openai_output))

    if openai_output["phrases"] == []:
        api_response, video_titles = yt.scrape_channels_through_api(youtube, openai_output["topic"], n)

        sorted_channels = yt.sort_channels(api_response)
        cleaned = yt.remove_duplicate_channels(sorted_channels)
        with_video_titles = yt.add_video_title_info(video_titles, cleaned)

    elif openai_output["phrases"] != []:
        channels_api_response = {"items": []}
        
        video_titles = {}
        for phrase in openai_output["phrases"]:
            api_response, _video_titles = yt.scrape_channels_through_api(youtube, phrase, n)
            video_titles.update(_video_titles)
            channels_api_response["items"] += api_response["items"]

        sorted_channels = yt.sort_channels(channels_api_response)
        cleaned = yt.remove_duplicate_channels(sorted_channels)
        with_video_titles = yt.add_video_title_info(video_titles, cleaned)

    else:
        print("Something went wrong")
    return with_video_titles


def select_relevant_channels(sorted_channels, init_query, f, t, top_n=25):
    unique_names = []
    for channel in sorted_channels:
        if channel["snippet"]["title"] not in unique_names:
            unique_names.append(channel["snippet"]["title"])

    channels_selected = []

    while len(channels_selected) < 3:
        for channel in sorted_channels[f:t]:
            if channel["snippet"]["title"] in unique_names:
                # Check whether relevant
                pt = load_prompt_template("check_if_relevant")
                prompt_check_relevant = pt.format(query=init_query, channel_info=channel["snippet"]["description"])
                is_relevant = call_openai(prompt_check_relevant)
                is_relevant = remove_openai_additions(is_relevant)
                is_relevant = json.loads(is_relevant)

                if is_relevant["relevant"] == "yes":
                    item = {}
                    item["title"] = channel["snippet"]["title"]
                    item["url"] = f"https://www.youtube.com/channel/{channel['id']}"
                    item["description"] = channel["snippet"]["description"]
                    item["statistics"] = channel["statistics"]
                    channels_selected.append(item)
                    unique_names.remove(channel["snippet"]["title"])

                elif is_relevant["relevant"] == "no":
                        continue

                else:
                    print("Warning. Something went wrong. Check is_relevant() function")
                    print(f"Model's output", is_relevant["relevant"])

            else:
                continue

        f = f + top_n
        t = t + top_n

    return channels_selected


def call_openai(prompt):
    load_dotenv()
    openai_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_key)

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt)
    return response.output_text
