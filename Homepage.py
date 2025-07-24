
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
        # if the captcha is wrong, the controllo session state is set to False and the captcha is regenerated
        st.session_state['controllo'] = False
        st.error("🚨 Oops, wrong answer, try again")

# define the function for the captcha control
def captcha_control():
    #control if the captcha is correct
    # if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
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
    st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_captcha))
    print("the captcha is: ", st.session_state['Captcha'])

    #setup the captcha widget
    image = ImageCaptcha(width=width, height=height)
    data = image.generate(st.session_state['Captcha'])
    col1.image(data)
    col1.text_input('Enter captcha text', key="captcha_input", on_change=verify_captcha)#, height=70)        
    st.button("Proceed to Login", on_click=verify_captcha)


def render_page_layout():
    # pass
    st.markdown(
        """
        <style>
    #             /* Prevent horizontal scroll globally */
    #     html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    #         overflow-x: hidden !important;
    #         max-width: 100vw !important;
    #     }

    #     *, *::before, *::after {
    #         box-sizing: border-box;
    #         max-width: 100%;
    #     }

    #     /* Scrollable fixed-height main area */
    #     [data-testid="stAppViewContainer"] {
    #         background: linear-gradient(to bottom right, #FFF9E5, #004030);
    #         overflow: hidden;
    #     }

    #     .main-content {
    #         max-height: 80vh;
    #         overflow-y: auto;
    #         padding-right: 15px;
    #     }

    #     # [data-testid="stSidebar"] > div:first-child {
    #     #     background-color: #004030; ##a1ffce;
    #     #     # color: #00ffcc;
    #     #     display: flex;
    #     #     flex-direction: column;
    #     #     height: 100vh;
    #     # }

        [data-testid="stSidebar"] ul li div a span {
            font-size: 18pt;
            color: #FFF9E5;
        }


    #     /* Set the color of all links */
    #     a {
    #         color: #00bfff !important; /* or "navy" as you wanted */
    #     }

    #     /* Make chat and other blocks readable */
    #     .stChatMessage,
    #     .stMarkdown,
    #     .stContainer {
    #         background-color: white; #rgba(255, 255, 255, 0.85); /* Light translucent background */
    #         color: #000000;
    #         max-width: 700px;          /* 👈 limits width */
    #         margin: 0 auto 1rem auto;  /* 👈 centers it */
    #         # border-radius: 12px;
    #         padding-right: 1rem;
    #         # margin-bottom: 1rem;
    #         text-align: justify;
            
    #     }

    #     .block-container > div:first-child {
    #         max-width: 700px;
    #         margin: 0 auto;
    #     }


    #     /* Optional: fix text input background too */
    #     textarea, .stTextInput > div > div > input {
    #         background-color: white; #rgba(255, 255, 255, 0.85) !important;
    #         color: black !important;
            
    #     }

    #     </style>
        """,
        unsafe_allow_html=True
    )

    # # Push the logout button to bottom
    # with st.sidebar:
    #     # st.markdown("### Navigation")
    #     # st.button("🔍 Explore")  # Example button

    #     st.markdown("<div style='flex: 1'></div>", unsafe_allow_html=True)

    #     # Logout button at bottom
    #     if st.button("Logout"):
    #         st.logout()
    #         st.rerun()


def get_credentials():
    host = st.session_state.redis_host
    port = st.session_state.redis_port
    password = st.session_state.redis_password
    return host, port, password

def create_connection(host, port, password):
    r = redis.Redis(host=host, port=port, 
                 db=0, decode_responses=True,
                 username='default', password=password)
    try:
        r.ping()
        return r
    except redis.exceptions.ConnectionError:
        return "xui"
    
def render_chat_history(memory):
    
    for msg in memory[-10:]:# Render assistant response immediately
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    st.markdown(msg["content"][0]["text"])
                else:    # if not st.session_state.get("Captcha"):
                    st.markdown(msg["content"])

def get_memory(r):
    msg_from_db = r.lrange(st.user.email+":memo", 0, -1)
    print("MSG FROM DB", msg_from_db)

    # if msg_from_db == []:
        # r.rpush(st.user.email+":memo", json.dumps({"content": [{"type": "text", "text": "I am an agent that helps you find YouTube channels"}], "role":"assistant"}))
        # memory = [{"content": [{"type": "text", "text": "I am an agent that helps you find YouTube channels"}], "role":"assistant"}]
    # else:
    memory = [json.loads(msg) for msg in msg_from_db]
    return memory
    
def chat(r):
    
    render_page_layout()
    st.title("📺 YouTube Channel Navigator")

    ### REDIS INIT
    ### GET INFO BY HASH OR CREATE A NEW ENTRY
    memory = get_memory(r)
    render_chat_history(memory)

    user_query = st.chat_input("Enter your query")
    
    if memory[-1]["role"] == "user":
        #run OpenAI
        with st.spinner("..."):

            func = st.session_state.agent.determine_function(memory[-4:])

            if func is None:
                f_name = "general_query"
            else:
                f_name = func.name
                msg_count = r.hget(st.user.email, "msg_count")
                print(msg_count)
                r.hset(st.user.email, mapping={"msg_count": int(msg_count)+1})
                # st.session_state.msg_count += 1
            
            f = st.session_state.agent.functions_registry()[f_name]

            if f_name == "general_query":
                answer = f(memory[-4:])
            else:
                answer = f(st.session_state.agent.query)  

            print("Assistant:", answer)
            ### APPEND
            r.rpush(st.user.email+":memo", json.dumps(st.session_state.agent.make_text_msg("assistant", answer)))
            print("PUSHED")
            st.rerun()

    elif memory[-1]["role"] == "assistant":
        if user_query:
            print("USER QUERY", user_query)
            st.session_state.last_active = time.time() # TO REDIS
            st.session_state.agent.query = user_query
            message = st.session_state.agent.make_text_msg("user", st.session_state.agent.query)
            r.rpush(st.user.email+":memo", json.dumps(message))
            st.rerun()
    #   text_input()
# else:
    # ..   
    st_autorefresh(interval=15 * 1000, key="auto_refresh")
    
    # if st.session_state.last_active:
    #     inactive_seconds = (datetime.now() - st.session_state.last_active).total_seconds()
    #     if inactive_seconds > 10:
    #         clean_session()
    #         st.rerun()
    # if msg_count > 3:
    #     over_limit()


def old_clean_session():
    st.session_state.controllo = False
    st.session_state.auth = False
    r.hset(st.user.email, mapping={"last_active": time.time()})
    r.hset(st.user.email, mapping={"block": -1, "msg_count": 0})
    st.logout()

def clean_session():
    st.session_state.controllo = False
    st.session_state.auth = False
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
        print("ZERO")
        r.hset(st.user.email, mapping={"block": time.time()})

    inactive_seconds = round(time.time() - int(float(blocked_at)))
    if inactive_seconds > 30:
        clean_session()
        st.rerun()

# Session state initialization
if "last_active" not in st.session_state:
    st.session_state.last_active = time.time()
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
                     "block": -1,
                     "auth": 1,
                     }


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


if not st.user.is_logged_in:
    if st.session_state['controllo'] == False:
        captcha_control()
    else: 
        render_page_layout()
        st.login("google")
        st.stop()
else:  # logged in
    host, port, password = get_credentials()
    r = create_connection(host, port, password)
    try:
        user_in_db = r.hgetall(st.user.email)

        if not user_in_db:
            r.hset(st.user.email, mapping=default_db_params)
            r.rpush(st.user.email+":memo", json.dumps({"content": [{"type": "text", "text": "I am an agent that helps you find YouTube channels"}], "role":"assistant"}))

        inactive = time.time() - st.session_state.last_active
        if inactive > 65:
            clean_session()
            st.rerun()

        timeout = r.hget(st.user.email, "msg_count")
        print("TIMEOUT", timeout)

        if int(timeout) < 3:
            chat(r)
        else:
            blocked_at = r.hget(st.user.email, "block")
            if int(float(blocked_at)) == -1:
                blocked_at = time.time()
                r.hset(st.user.email, mapping={"block": blocked_at})
            over_limit(blocked_at)
            
    finally:
        del r

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
# st.logout()