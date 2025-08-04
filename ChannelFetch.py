import os
import json
import random
import string
import time
from datetime import datetime

import redis
import streamlit as st
from captcha.image import ImageCaptcha
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

import agent.agent_core as ac




def verify_captcha():
    col1, col2, _ = st.columns(3)
    if st.session_state.captcha_input.lower() == st.session_state["Captcha"].lower():
        col1.empty()
        col2.empty()
        st.session_state['controllo'] = True
        st.success("Verification successful. Welcome!")
        
        time.sleep(1)
        st.rerun()
    else:
        st.session_state['controllo'] = False
        st.error("🚨 Oops, wrong answer, try again")


def captcha_control():
    render_page_layout()
    st.header("ChannelFetch 📺")
    st.html("""<div style="text-align: justify;">
            <strong>Tired of endless scrolling on YouTube? Let ChannelFetch come into play!</strong>

            <p>
            With Channel Fetch, you can:<br>
            1. Get a YouTube channels selection with a summary. Try asking "Find channels about traveling".<br>
            2. Get quick overviews of a channel's content from video titles, for example, "What is this channel about?"<br>
            3. Run regular searches like "video tips for baking"<br>
            4. Ask a model simple questions in chat format
            </p>


            <p>
            ChannelFetch uses OpenAI models and the YouTube Data API to find channels that match your interests, 
            so you can skip the noise and get straight to the good stuff.
            </p>

            <p><strong>Ready to start?</strong></p>
            </div>""")

    st.markdown("Please verify that you are a human")
    
    col1, col2, _ = st.columns(3)
    length_captcha = 4
    st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_captcha))
    print("the captcha is: ", st.session_state['Captcha'])

    
    width = 250
    height = 45
    image = ImageCaptcha(width=width, height=height)
    data = image.generate(st.session_state['Captcha'])
    col1.image(data)
    col1.text_input('Enter captcha text', key="captcha_input", on_change=verify_captcha)#, height=70)        
    st.button("Proceed to Google Login", on_click=verify_captcha)


def render_page_layout():
    
    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] ul li div a span {
            font-size: 18pt;
            color: #FFF9E5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def get_credentials():
    host = st.secrets["redis"]["redis_host"]
    port = st.secrets["redis"]["redis_port"]
    password = st.secrets["redis"]["redis_password"]
    openai = str(st.secrets["api_keys"]["openai_key"])
    yt = str(st.secrets["api_keys"]["youtube_key"])
    return host, port, password, openai, yt


def create_connection(host, port, password):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
        return r
    except redis.exceptions.ConnectionError:
        return "x"
    

def render_chat_history(memory):
    for msg in memory[-10:]:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    st.markdown(msg["content"][0]["text"])
                else:
                    st.markdown(msg["content"])


def get_memory(r):
    msg_from_db = r.lrange(st.user.email+":memo", 0, -1)
    memory = [json.loads(msg) for msg in msg_from_db]
    return memory
    

def chat(r, openai_key, yt_key):
    
    # render_page_layout()
    st.title("📺 ChannelFetch")

    memory = get_memory(r)
    render_chat_history(memory)

    user_query = st.chat_input("Enter your query")
    
    if memory[-1]["role"] == "user":
        with st.spinner("..."):

            func = st.session_state.agent.determine_function(memory[-4:])

            if func is None:
                f_name = "general_query"
            else:
                f_name = func.name
                msg_count = r.hget(st.user.email, "msg_count")
                r.hset(st.user.email, mapping={"msg_count": int(msg_count)+1})
            
            f = st.session_state.agent.functions_registry()[f_name]

            if f_name == "general_query":
                answer = f(memory[-4:])
            else:
                answer = f(st.session_state.agent.query)  

            r.rpush(st.user.email+":memo", json.dumps(st.session_state.agent.make_text_msg("assistant", answer)))
            st.rerun()

    elif memory[-1]["role"] == "assistant":
        if user_query:
            st.session_state.last_active = time.time() # TO REDIS
            st.session_state.agent.query = user_query
            message = st.session_state.agent.make_text_msg("user", st.session_state.agent.query)
            r.rpush(st.user.email+":memo", json.dumps(message))
            st.rerun()

    else:
        st.rerun()

    st_autorefresh(interval=15 * 1000, key="auto_refresh")


def clean_session():
    st.session_state.controllo = False
    st.session_state.last_active = time.time()
    r.delete(st.user.email)
    r.delete(st.user.email+":memo")
    st.logout()


def over_limit(blocked_at):
    render_page_layout()
    memory = get_memory(r)
    render_chat_history(memory)
    with st.chat_message("assistant"):
        st.markdown("Oops! You've reached the limit of free requests. This app is free to use, and we want to ensure fair access for everyone. You'll be able to log in and chat again in about an hour. Thank you for your understanding!")
    
    if int(float(blocked_at)) == 0:
        r.hset(st.user.email, mapping={"block": time.time()})

    inactive_seconds = round(time.time() - int(float(blocked_at)))
    if inactive_seconds > 900:
        clean_session()
        st.rerun()


st.set_page_config(page_title="Channel Fetch")

# Session state initialization
host, port, password, openai_key, yt_key = get_credentials()

if "last_active" not in st.session_state:
    st.session_state.last_active = time.time()
if "agent" not in st.session_state:
    load_dotenv()
    st.session_state.agent = ac.YTNavigatorAgent("", openai_key, yt_key)
if "controllo" not in st.session_state:
    st.session_state.controllo = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "redis_host" not in st.session_state:
    load_dotenv()
    st.session_state.redis_host = os.environ.get("REDIS_HOST")
    st.session_state.redis_port = os.environ.get("REDIS_PORT")
    st.session_state.redis_password = os.environ.get("REDIS_PASSWORD")

default_db_params = {
                     "last_active": time.time(),
                     "msg_count": 0,
                     "block": -1,
                     "auth": 1
                     }


if not st.user.is_logged_in:
    if st.session_state['controllo'] == False:
        captcha_control()

    else: 
        render_page_layout()
        r = create_connection(host, port, password)
        st.login("google")     
        st.stop()
elif st.user.is_logged_in and (time.time() - st.user.iat) > 3600:
    st.logout()
else:  # logged in

    r = create_connection(host, port, password)
    try:
        user_in_db = r.hgetall(st.user.email)

        if not user_in_db:
            r.hset(st.user.email, mapping=default_db_params)
            r.rpush(st.user.email+":memo", json.dumps({"content": [{"type": "text", "text": "I am an agent that helps you find YouTube channels"}], "role":"assistant"}))
            r.expire(st.user.email, 3600)
            r.expire(st.user.email+":memo", 3600)

        inactive = time.time() - st.session_state.last_active
        if inactive > 3600:
            clean_session()
            st.rerun()

        timeout = r.hget(st.user.email, "msg_count")

        if int(timeout) < 12:
            chat(r, openai_key, yt_key)
        else:
            blocked_at = r.hget(st.user.email, "block")
            if int(float(blocked_at)) == -1:
                blocked_at = time.time()
                r.hset(st.user.email, mapping={"block": blocked_at})
            over_limit(blocked_at)
            
    finally:
        del r