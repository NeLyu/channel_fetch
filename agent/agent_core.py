from agent.utils.prompt_loader import load_prompt_template
import agent.utils.youtube_utils as yt
from openai import OpenAI
from dotenv import load_dotenv
import os, json, sys


class YTNavigatorAgent:
    def __init__(self, query, api_key):
        self.query = query
        self.youtube = yt.build_youtube_client(api_key)
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
                    item = {}
                    item["title"] = channel["snippet"]["title"]
                    item["url"] = f"https://www.youtube.com/channel/{channel['id']}"
                    item["description"] = channel["snippet"]["description"]
                    item["video_title"] = channel["snippet"]["video_title"]
                    item["videoId"] = f"https://www.youtube.com/watch?v={channel['snippet']['videoId']}"
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

        return channels_selected


    def call_openai(self, messages):
        load_dotenv()
        openai_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_key)
        messages = [self.s_template] + messages
        response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages
                        
                    )
        return response.choices[0].message.content

    def search_channels(self, query):    
        pt = load_prompt_template("process_query")

        m = self.make_text_msg("user", pt.format(query=query))
        messages = [self.s_template, m]

        extended_query = self.call_openai(messages)

        print("Extracting channels...")
        n = 10
        sorted_channels = self.extract_channels(extended_query, n)

        print("Selecting only relevant channels...")
        channels_selected = self.select_relevant_channels(sorted_channels, query)

        if len(channels_selected) < 2:
            print("Expanding search...")
            n = 15
            sorted_channels = self.extract_channels(extended_query, n)
            channels_selected = self.select_relevant_channels(sorted_channels, query)

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
        
        print("Recommended channels:")
        answer = []
        for i in range(top_to_show):
            print(f"""{i + 1}. {channels_selected[i]["title"]}""")
            print(channels_selected[i]["url"])
            print(f"Treding video from the channel:")
            print(channels_selected[i]["video_title"])
            print(channels_selected[i]["videoId"])
            print()

        print()
        return summary


    def channels_recent_videos_overview(self):
        pass

    def personalizing(self):
        pass

    def general_query(self, messages):
        response = self.call_openai(messages)
        return response

    def determine_function(self, messages):
        with open('./prompts/functions_descriptions.json', 'r') as file:
            functions = json.load(file)

        openai_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_key)

        response = client.chat.completions.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call="auto",
        )

        tool_call = response.choices[0].message.function_call
        return tool_call

    def functions_registry(self):
        registry = {
                    "search_channels": self.search_channels,
                    "general_query": self.general_query
                    }
        return registry
