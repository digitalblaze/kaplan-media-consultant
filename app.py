import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from prompt import SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
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

/* Canned prompt buttons */
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

with st.sidebar:
    st.markdown("## Tools")
    for tool in TOOLS:
        st.markdown(f"**[{tool['name']}]({tool['url']})**")
        st.caption(tool["desc"])
        st.divider()
    st.caption(f"Signed in as {st.experimental_user.email}")
    st.button("Sign out", on_click=st.logout, use_container_width=True)

if not st.experimental_user.is_logged_in:
    st.title("Kaplan Media Consultant")
    st.markdown("Sign in with your Kaplan Google account to continue.")
    st.button("Sign in with Google", on_click=st.login, args=["google"])
    st.stop()

email = st.experimental_user.email or ""
if not (email.endswith("@kaplan.com") or email.endswith("@kaplan.edu")):
    st.error(f"Access is restricted to @kaplan.com and @kaplan.edu accounts. You signed in as **{email}**.")
    st.button("Sign out", on_click=st.logout)
    st.stop()

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
