from agent.utils.youtube_utils import build_youtube_client
from agent.utils.prompt_loader import load_prompt_template
import agent.utils.youtube_utils as yt
import agent.agent_core as ac
from time import time
from dotenv import load_dotenv
import os, json
from pprint import pprint
import sys

def main():
    load_dotenv()
    api_key = os.environ.get("YT_API_KEY")
    agent = ac.YTNavigatorAgent("", api_key)
    youtube = yt.build_youtube_client(api_key)

    while True:
        query = input("User: ")
        agent.query = query
        message = agent.make_text_msg("user", agent.query)

        agent.memory.append(message)

        func = agent.determine_function(agent.memory[-4:])
        print(func)

        if func is None:
            f_name = "general_query"
        else:
            f_name = func.name
        
        f = agent.functions_registry()[f_name]

        if f_name == "general_query":
            answer = f(agent.memory[-4:])
        else:
            answer = f(json.loads(func.arguments)["full_prompt"])  

        print("Assistant:", answer)
        agent.memory.append(agent.make_text_msg("assistant", answer))


if __name__ == "__main__":
    main()