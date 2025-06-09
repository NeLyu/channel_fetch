from agent.utils.youtube_utils import build_youtube_client
from agent.utils.prompt_loader import load_prompt_template
import agent.agent_core as ac
from time import time
from dotenv import load_dotenv
import os, json
from pprint import pprint
import sys

def main():
    load_dotenv()
    api_key = os.environ.get("YT_API_KEY")
    youtube = build_youtube_client(api_key)

    query = input("Type your query: ")
    
    pt = load_prompt_template("process_query")
    prompt_w_query = pt.format(query=query)
    extended_query = ac.call_openai(prompt_w_query)

    print("Extracting channels...")
    n = 30
    sorted_channels = ac.extract_channels(extended_query, youtube, n)

    print("Selecting only relevant channels...")
    channels_selected = ac.select_relevant_channels(sorted_channels, query, 0, 25)
    print()

    print("Summarizing...")
    pt = load_prompt_template("summarize")
    prompt_for_summary = pt.format(query=query, channels_selected=channels_selected)
    summary = ac.call_openai(prompt_for_summary)
    print("Recommended channels:")
    for i in range(len(channels_selected)):
        print(f"""{i + 1}. {channels_selected[i]["title"]}""")
        print(channels_selected[i]["url"])

    print()
    print(summary)

if __name__ == "__main__":
    a = time()
    main()
    print(time()-a)