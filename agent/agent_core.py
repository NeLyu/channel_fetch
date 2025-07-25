from agent.utils.prompt_loader import load_prompt_template
import agent.utils.youtube_utils as yt
from openai import OpenAI
from dotenv import load_dotenv
import os, json, sys
from pprint import pprint
import streamlit as st

class YTNavigatorAgent:
    def __init__(self, query, openai_key=None, ytapi_key=None):
        self.query = query
        self.ytapi_key = ytapi_key
        self.youtube = yt.build_youtube_client(self.ytapi_key)
        self.openai_key = openai_key
        self.s_template = {"role": "system",
                            "content": load_prompt_template("sys_prompt")}
            
        self.memory = []


    def make_text_msg(self, role, text):
        return {
            "role": role,
            "content": [{"type": "text", "text": text}]
        }

    def remove_openai_additions(self, openai_output):
        openai_output = openai_output.replace("```json\n", "")
        openai_output = openai_output.replace("```", "")
        return openai_output

    def extract_channels(self, openai_output, n):
        openai_output = json.loads(self.remove_openai_additions(openai_output))

        if openai_output["phrases"] == []:
            n = 30
            api_response, video_titles = yt.scrape_channels_through_api(self.youtube, openai_output["topic"], n)
            sorted_channels = yt.sort_channels(api_response)
            cleaned = yt.remove_duplicate_channels(sorted_channels)
            with_video_titles = yt.add_video_title_info(video_titles, cleaned)

        elif openai_output["phrases"] != []:
            channels_api_response = {"items": []}
            video_titles = {}
            for phrase in openai_output["phrases"]:
                api_response, _video_titles = yt.scrape_channels_through_api(self.youtube, phrase, n)
                video_titles.update(_video_titles)
                channels_api_response["items"] += api_response["items"]

            sorted_channels = yt.sort_channels(channels_api_response)
            cleaned = yt.remove_duplicate_channels(sorted_channels)
            with_video_titles = yt.add_video_title_info(video_titles, cleaned)

        else:
            print("Something went wrong")
        return with_video_titles


    def select_relevant_channels(self, sorted_channels, init_query):
        unique_names = []
        for channel in sorted_channels:
            if channel["snippet"]["title"] not in unique_names:
                unique_names.append(channel["snippet"]["title"])

        channels_selected = []

        for channel in sorted_channels:
            if channel["snippet"]["title"] in unique_names:
                # Check whether relevant
                pt = load_prompt_template("check_if_relevant")
                m = self.make_text_msg("user", pt.format(query=init_query, channel_info=channel["snippet"]["description"]))
                messages = [self.s_template, m]
                is_relevant = self.call_openai(messages)
                is_relevant = self.remove_openai_additions(is_relevant)
                is_relevant = json.loads(is_relevant)

                if is_relevant["relevant"] == "yes":
                    item = self.extract_channel_info_for_summary(channel)
                    channels_selected.append(item)
                    unique_names.remove(channel["snippet"]["title"])

                elif is_relevant["relevant"] == "no":
                        continue

                else:
                    print("Warning. Something went wrong. Check is_relevant() function")
                    print(f"Model's output", is_relevant["relevant"])

            else:
                continue

        return channels_selected

    def select_relevant_channels_in_batch(self, sorted_channels, init_query):
        pt = load_prompt_template("check_if_relevant_in_batch")
        channel_info = ""
        for ch in sorted_channels:
            channel_info += "Channel name: " + ch["snippet"]["title"] + "\n"
            channel_info += "Channel description: " + ch["snippet"]["description"] + "\n\n"
            
        pt = load_prompt_template("check_if_relevant_in_batch")
        m = self.make_text_msg("user", pt.format(query=init_query, channel_info=channel_info))
        messages = [self.s_template, m]
        relevant = self.call_openai(messages)
        relevant = self.remove_openai_additions(relevant)
        relevant = json.loads(relevant)
        return relevant


    def extract_channel_info_for_summary(self, channel):
        item = {}
        item["title"] = channel["snippet"]["title"]
        item["url"] = f"https://www.youtube.com/{channel['id']}"
        item["description"] = channel["snippet"]["description"]
        item["video_title"] = channel["snippet"]["video_title"]
        item["videoId"] = f"https://www.youtube.com/watch?v={channel['snippet']['videoId']}"
        item["statistics"] = channel["statistics"]
        return item

    def call_openai(self, messages):
        load_dotenv()
        # openai_key = #os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=self.openai_key)
        messages = [self.s_template] + messages
        response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                        
                    )
        return response.choices[0].message.content

    def create_message_for_summary(self, top_to_show, channels_selected, summary):
        message = ""
        for i in range(top_to_show):
            message += f"""{i + 1}. {channels_selected[i]["snippet"]["title"]}\n"""
            message += f"""https://www.youtube.com/{channels_selected[i]["snippet"]["customUrl"]}\n"""
            message += f"\nTrending video from the channel:" + "\n"
            message += channels_selected[i]["snippet"]["video_title"] + "\n"
            message += f"""https://www.youtube.com/watch?v={channels_selected[i]["snippet"]["videoId"]}\n\n"""
        
        message += summary
        return message

    def search_channels(self, query):    
        pt = load_prompt_template("process_query")

        m = self.make_text_msg("user", pt.format(query=query))
        messages = [self.s_template, m]

        extended_query = self.call_openai(messages)

        print("Extracting channels...")
        n = 10
        sorted_channels = self.extract_channels(extended_query, n)

        print("Selecting only relevant channels...")
        relevant = self.select_relevant_channels_in_batch(sorted_channels, query)


        if len(relevant["relevant_channels"]) < 2:
            print("Expanding search...")
            n = 15
            sorted_channels = self.extract_channels(extended_query, n)
            relevant = self.select_relevant_channels_in_batch(sorted_channels, query)

        channels_selected = [ch for ch in sorted_channels if ch["snippet"]["title"] in relevant["relevant_channels"]]

        if len(channels_selected) == 0:
            return "Sorry, I couldn’t find any relevant YouTube channels for this query. Try rephrasing it?"

        print("Summarizing...")
        pt = load_prompt_template("summarize")

        m = self.make_text_msg("user", pt.format(query=query, channels_selected=channels_selected))
        messages = [self.s_template, m]
        summary = self.call_openai(messages)

        top_to_show = 5
        if len(channels_selected) < top_to_show:
            top_to_show = len(channels_selected)
        
        answer = self.create_message_for_summary(top_to_show, channels_selected, summary)
        return answer


    def channels_recent_videos_overview(self, name):

        channel_info = yt.channel_info_by_name(name, self.youtube)
        titles_with_metadata = yt.get_video_titles(channel_info[name]["ID"], self.youtube)
        
        titles = ""
        for el in titles_with_metadata:
            titles += el["title"] + "\n"

        pt = load_prompt_template("summarize_titles")
        m = self.make_text_msg("user", pt.format(titles=titles))
        messages = [self.s_template, m]
        summary = self.call_openai(messages)

        answer = summary + f"""\n\nCheck it out here https://www.youtube.com/{channel_info[name]["customUrl"]}/videos"""
        return answer

    def personalizing(self):
        pass

    def general_query(self, messages):
        response = self.call_openai(messages)
        return response

    def determine_function(self, messages):
        with open('./prompts/functions_descriptions.json', 'r') as file:
            functions = json.load(file)

        # openai_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=self.openai_key)

        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )

        tool_call = response.choices[0].message.function_call
        return tool_call

    def search_videos_by_key_phrase(self, query):
        video_results, video_titles = yt.top_videos_by_keyword(self.youtube, query, 10, order="rating")
        answer = ""
        for item in video_results["items"]:
            answer += item["snippet"]["title"] + "\n"
            answer += "https://www.youtube.com/watch?v=" + item["id"]["videoId"] + "\n\n"
        return answer

    def functions_registry(self):
        registry = {
                    "search_channels": self.search_channels,
                    "general_query": self.general_query,
                    "channels_recent_videos_overview": self.channels_recent_videos_overview,
                    "search_videos_by_key_phrase": self.search_videos_by_key_phrase
                    }
        return registry
