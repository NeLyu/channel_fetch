
# from streamlit_oauth import OAuth2Component
from agent.utils.youtube_utils import build_youtube_client
from agent.utils.prompt_loader import load_prompt_template
import agent.agent_core as ac
import streamlit as st
import redis

from dotenv import load_dotenv
import os, json
from pprint import pprint
import sys
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# for chaptcha
from captcha.image import ImageCaptcha
import random, string
from time import time
import time



# define the function for the captcha control
def captcha_control():

    #control if the captcha is correct
    if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
        # define the costant
        length_captcha = 4
        width = 250
        height = 45

        render_page_layout()
        
        st.header("YouTube Channel Navigator 📺")
        st.markdown("Please verify that you are a human")
        
        # define the session state for control if the captcha is correct
        # st.session_state['controllo'] = False
        col1, col2, _ = st.columns(3)
        
        # define the session state for the captcha text because it doesn't change during refreshes 
        if 'Captcha' not in st.session_state or st.session_state.hold == True:
            print("!!!")
        st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_captcha))
        st.session_state["captcha_tries"].append(st.session_state['Captcha'])
        print("the captcha is: ", st.session_state['Captcha'])

        #setup the captcha widget
        image = ImageCaptcha(width=width, height=height)
        data = image.generate(st.session_state['Captcha'])
        col1.image(data)
        print("Before click")
        capta2_text = col1.text_input('Enter captcha text', key="captcha_input")#, height=70)
        print(capta2_text)
        # time.sleep(5)
        
        
        if capta2_text or st.button("Proceed to Login"):
            print("After click")
            # print(capta2_text, st.session_state['Captcha'])
            capta2_text = capta2_text.replace(" ", "")
            # st.sessions_state.hold = True

            # if the captcha is correct, the controllo session state is set to True
            # if len(st.session_state.captcha_tries) == 1:
                # if st.session_state['Captcha'].lower() == capta2_text.lower().strip():
            if st.session_state.captcha_tries[-2].lower() == capta2_text.lower().strip():
                col1.empty()
                col2.empty()
                st.session_state['controllo'] = True
                st.session_state.just_verified = True
                st.success("Verification successful. Welcome!")
                
                time.sleep(1)
                st.rerun()
            else:
                # if the captcha is wrong, the controllo session state is set to False and the captcha is regenerated
                st.session_state['controllo'] = False
                st.error("🚨 Oops, wrong answer, try again")
                
        else:
            #wait for the button click
            st.stop()

def authorize():
    # if 'auth' not in st.session_state or st.session_state['auth'] == False:
    if not st.user.is_logged_in:
        st.login("google")
        # st.rerun()
    # else:
    st.stop()

    # if st.button("Log out"):
        # st.logout()
    
    # st.markdown(f"Welcome! {st.user.name}")
    
def render_page_layout():
    st.markdown(
            """
            <style>
            # .stApp {
            #     background: linear-gradient(to bottom right, #a1ffce, #ffd5ec);
            #     color: black;
                
            # }
            
            [data-testid="stAppViewContainer"]{
                background: linear-gradient(to bottom right, #a1ffce, #0f141e);
                color: black;
            [data-testid="stSidebar"]> div:first-child{
                background-color: #0f141e;
            # [data-testid="stBottom"]> div:nth-child(2) {
            #     background-color: #ffd5ec;
            }
            
            </style>
            """,
            unsafe_allow_html=True
        )

def render_chat_history(memory):
    # for msg in st.session_state.memory[:-2]:  # Skip last user + assistant
    for msg in memory[:-2]:    
        with st.chat_message(msg["role"]):
            content = msg["content"]
            if isinstance(content, list):
                st.markdown(content[0]["text"])
            else:
                st.markdown(content)

def redis_get(host, port, password, key, attribute=False):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        return "xui"
    
    try:
        if attribute:
            value = r.hget(key, attribute)
        else:
            value = r.hgetall(key)
    finally:
        del r
    return value


def redis_set(host, port, password, key, values_dict):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        return "xui"
    
    try:
        r.hset(key, mapping=values_dict)
    finally:
        del r  
    

def redis_push(host, port, password, key, value):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        return "xui"
    
    try:
        r.rpush(key+":memo", value)
    finally:
        del r

def redis_lrange(host, port, password, key):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
    except redis.exceptions.ConnectionError:
        return "xui"
    
    try:
        messages = r.lrange(key+":memo", 0, -1)
    finally:
        del r    
    return messages

def get_credentials():
    host = st.session_state.redis_host
    port = st.session_state.redis_port
    password = st.session_state.redis_password
    return host, port, password


def main():
    
    render_page_layout()
    st.title("📺 YouTube Channel Navigator")

    ### REDIS INIT
    ### GET INFO BY HASH OR CREATE A NEW ENTRY
    host, port, password = get_credentials()
    msg_from_db = redis_lrange(host, port, password, st.user.email)
    if not msg_from_db:
        memory = []
    memory = [json.loads(msg) for msg in msg_from_db]

    user_query = st.chat_input("Enter your query")
    
    for msg in memory:# Render assistant response immediately
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    st.markdown(msg["content"][0]["text"])
                else:    # if not st.session_state.get("Captcha"):
                    st.markdown(msg["content"])

    if user_query and st.session_state.block == False:
        # Render user message immediately
        with st.chat_message("user"):
            st.markdown(user_query)

        st.session_state.last_active = datetime.now()
        st.session_state.agent.query = user_query
        message = st.session_state.agent.make_text_msg("user", st.session_state.agent.query)
        print(message)
        memory.append(message) #message)
        print(memory)
        
        redis_push(host, port, password, st.user.email, json.dumps(message))

        with st.spinner("..."):

            func = st.session_state.agent.determine_function(memory[-4:])

            if func is None:
                f_name = "general_query"
                v = redis_get(host, port, password, st.user.email, "msg_count")
                print(v)
                print(type(v))
                redis_set(host, port, password, st.user.email, {"msg_count": int(v)+1})
                # st.session_state.msg_count += 1
            else:
                f_name = func.name
                v = redis_get(host, port, password, st.user.email, "msg_count")
                print(v)
                print(type(v))
                redis_set(host, port, password, st.user.email, {"msg_count": int(v)+1})
                # st.session_state.msg_count += 1
            
            f = st.session_state.agent.functions_registry()[f_name]

            if f_name == "general_query":
                # answer = f(st.session_state.memory[-4:])
                answer = f(memory[-4:])
            else:
                answer = f(st.session_state.agent.query)  

            print("Assistant:", answer)

            ### APPEND
            redis_push(host, port, password, st.user.email, json.dumps(st.session_state.agent.make_text_msg("assistant", answer)))
            # st.session_state.memory.append(st.session_state.agent.make_text_msg("assistant", answer))
            # Render assistant response immediately
            with st.chat_message("assistant"):
                st.markdown(answer if isinstance(answer, str) else answer[0]["text"])

            
    st_autorefresh(interval=15 * 1000, key="auto_refresh")
        
    if st.session_state.last_active:
        inactive_seconds = (datetime.now() - st.session_state.last_active).total_seconds()
        if inactive_seconds > 25:
            clean_session()
            st.rerun()
    if st.session_state.msg_count > 3:
        over_limit()

    ### DEL REDIS


def clean_session():
    st.session_state.just_verified = False
    st.session_state.controllo = False
    st.session_state.auth = False
    st.session_state.last_active = datetime.now()
    st.session_state.memory = []
    st.session_state.block = False
    st.logout()

def over_limit():
    st.session_state.block = True
    render_page_layout()
    st.markdown("Oops! You've reached the limit of free requests. This app is free to use, and we want to ensure fair access for everyone. You'll be able to log in and chat again in about an hour. Thank you for your understanding!")
    st_autorefresh(interval=15 * 1000, key="auto_refresh_2")
        
    if st.session_state.last_active:
        inactive_seconds = (datetime.now() - st.session_state.last_active).total_seconds()
        if inactive_seconds > 35:
            clean_session()
            st.rerun()

# Session state initialization
if "last_active" not in st.session_state:
    st.session_state.last_active = datetime.now()
if "memory" not in st.session_state:
    st.session_state.memory = []
if "agent" not in st.session_state:
    load_dotenv()
    api_key = os.environ.get("YT_API_KEY")
    st.session_state.agent = ac.YTNavigatorAgent("", api_key)
if "just_verified" not in st.session_state:
    st.session_state.just_verified = False
if "controllo" not in st.session_state:
    st.session_state.controllo = False
if 'Captcha' not in st.session_state:
    st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) #length_captcha))
if "captcha_tries" not in st.session_state:
    st.session_state.captcha_tries = [st.session_state["Captcha"], st.session_state["Captcha"]]
if "hold" not in st.session_state:
    st.session_state.hold = False 
if "auth" not in st.session_state:
    st.session_state.auth = False
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0
if "block" not in st.session_state:
    st.session_state.block = False
if "redis_host" not in st.session_state:
    load_dotenv()
    st.session_state.redis_host = os.environ.get("REDIS_HOST")
    st.session_state.redis_port = os.environ.get("REDIS_PORT")
    st.session_state.redis_password = os.environ.get("REDIS_PASSWORD")


default_db_params = {
                    # "memory": ,
                     "last_active": time.time(),
                     "msg_count": 0,
                     "block": 0,
                     "auth": 1}


st.write('Random %d' % (random.randint(1,14234)) )
st.html(
f"""
<pre>
{"\n".join([str(k)+":"+str(v) for k,v in st.session_state.items()])}
</pre>
<pre>
USER: {[str(k)+":"+str(v) for k,v in st.user.items()]}
</pre>
"""
)


# str(st.user.name
  # 3 minutes
# # Now check if CAPTCHA is passed print(st.user.email)
# if st.user.is_logged_in:
#     v = redis_get(st.session_state.redis_host, st.session_state.redis_port, st.session_state.redis_password, st.user.email)
#     print("KEY in DB", v)
#     if not v:
#         host, port, password = get_credentials()
#         redis_set(host, port, password,
#               st.user.email,
#               default_db_params
#               )
#         redis_push(host, port, password,
#               st.user.email, "")

    # print(st.user.email)

if not st.user.is_logged_in:
    if st.session_state['controllo'] == False:
        captcha_control()
    else: #st.session_state['controllo'] != False:
        # st.session_state.controllo = False
        render_page_layout()
        
        st.login("google")
        st.stop()
    # print("!!!!!")
    # time.sleep(2)
    # redis_set(st.session_state.redis_host,
    #           st.session_state.redis_port,
    #           st.session_state.redis_password,
    #           st.user.name,
    #           default_db_params
    #           )
    
    # print(redis_get(st.user.name))
    # print("After login")
    hash = "HASH"
    ### CREATE ENTRY
    ## -->
    # st.stop()
else:
    if st.session_state.block == True:
        over_limit()
    else:
        main()