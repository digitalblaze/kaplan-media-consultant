import os
import urllib.parse
import streamlit as st
import google.generativeai as genai
import requests as http_requests
from dotenv import load_dotenv
from prompt import SYSTEM_PROMPT

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or st.secrets.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or st.secrets.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI") or st.secrets.get("REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)

st.set_page_config(
    page_title="Kaplan Media Consultant",
    page_icon="🎬",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Open+Sans:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Open Sans', Arial, sans-serif;
    color: #212121;
}

h1, h2, h3 {
    font-family: 'Merriweather', Georgia, serif;
    font-weight: 300;
    color: #240F6E;
}

header[data-testid="stHeader"] {
    background-color: #240F6E;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Open Sans', Arial, sans-serif;
    border: 1.5px solid #240F6E;
    border-radius: 8px;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #EFEFEF;
    border-radius: 8px;
    padding: 4px;
}

div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #F5F3FB;
    border-left: 4px solid #240F6E;
    border-radius: 8px;
    padding: 4px;
}

a {
    color: #240F6E;
    font-weight: 600;
}

div[data-testid="stAppViewBlockContainer"] h1 {
    color: #240F6E;
}

div[data-testid="stCaptionContainer"] p {
    color: #503F8B;
    font-family: 'Open Sans', Arial, sans-serif;
}

div[data-testid="stButton"] button {
    background-color: #F5F3FB;
    color: #240F6E;
    border: 1.5px solid #240F6E;
    border-radius: 8px;
    font-family: 'Open Sans', Arial, sans-serif;
    font-size: 0.85rem;
    text-align: left;
    white-space: normal;
    height: auto;
    padding: 10px 14px;
}

div[data-testid="stButton"] button:hover {
    background-color: #240F6E;
    color: #FFFFFF;
    border-color: #240F6E;
}
</style>
""", unsafe_allow_html=True)

TOOLS = [
    {
        "name": "Auto Subtitler",
        "url": "https://autosub.kapteach.com/",
        "desc": "Add captions & translate Brightcove videos",
    },
    {
        "name": "Frame.io → Smartsheet",
        "url": "https://frameio-smartsheet-sync-zfakvqtam89uyadhbybmbw.streamlit.app/",
        "desc": "Sync video assets from Frame.io into Smartsheet",
    },
    {
        "name": "Media Dashboard",
        "url": "https://media-dashboardgit-xgbe8e2jkyjf49nmaph7fj.streamlit.app/",
        "desc": "Project overview & AI morning briefing",
    },
    {
        "name": "KitHub",
        "url": "https://kitpath-hub-213102077280.us-central1.run.app/",
        "desc": "Equipment check-in/out & kit tracking",
    },
    {
        "name": "PM Agent",
        "url": "https://kaplan-pm-agent.vercel.app/",
        "desc": "AI assistant for master build plans",
    },
]

def get_login_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"

def exchange_code_for_email(code):
    resp = http_requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    })
    resp.raise_for_status()
    token = resp.json()
    userinfo = http_requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    userinfo.raise_for_status()
    return userinfo.json().get("email", "")

# --- AUTH GATE ---
if "authenticated_email" not in st.session_state:
    code = st.query_params.get("code")
    if code:
        with st.spinner("Signing you in..."):
            try:
                email = exchange_code_for_email(code)
                st.query_params.clear()
                if email.endswith("@kaplan.com") or email.endswith("@kaplan.edu"):
                    st.session_state.authenticated_email = email
                    st.rerun()
                else:
                    st.error(f"Access is restricted to @kaplan.com and @kaplan.edu accounts. You signed in as **{email}**.")
                    st.link_button("Try a different account", get_login_url())
                    st.stop()
            except Exception:
                st.error("Sign-in failed. Please try again.")
                st.link_button("Try again", get_login_url())
                st.stop()
    else:
        st.title("Kaplan Media Consultant")
        st.markdown("Sign in with your Kaplan Google account to continue.")
        st.link_button("Sign in with Google", get_login_url(), type="primary")
        st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## Tools")
    for tool in TOOLS:
        st.markdown(f"**[{tool['name']}]({tool['url']})**")
        st.caption(tool["desc"])
        st.divider()
    st.caption(f"Signed in as {st.session_state.authenticated_email}")
    if st.button("Sign out", use_container_width=True):
        del st.session_state.authenticated_email
        st.rerun()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Kaplan Media Consultant")
st.caption("Tell me what you're working on and I'll point you to the right tool.")

CANNED = [
    "I need to add subtitles to a video",
    "I need to sync Frame.io projects to Smartsheet",
    "Show me a status overview of all media projects",
    "I need to check out production equipment",
    "I'm a PM working on a master build plan",
    "I need to translate a video into another language",
]

if not st.session_state.messages:
    st.markdown("**Not sure where to start? Try one of these:**")
    cols = st.columns(2)
    for i, msg in enumerate(CANNED):
        if cols[i % 2].button(msg, use_container_width=True, key=f"canned_{i}"):
            st.session_state.pending_prompt = msg
            st.rerun()
    st.markdown("---")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("What do you need help with?")
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            history = [
                {
                    "role": "model" if m["role"] == "assistant" else "user",
                    "parts": [m["content"]],
                }
                for m in st.session_state.messages[:-1]
            ]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            reply = response.text
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
