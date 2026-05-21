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

/* Top header bar */
header[data-testid="stHeader"] {
    background-color: #240F6E;
}

/* Chat input */
div[data-testid="stChatInput"] textarea {
    font-family: 'Open Sans', Arial, sans-serif;
    border: 1.5px solid #240F6E;
    border-radius: 8px;
}

/* User message bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #EFEFEF;
    border-radius: 8px;
    padding: 4px;
}

/* Assistant message bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #F5F3FB;
    border-left: 4px solid #240F6E;
    border-radius: 8px;
    padding: 4px;
}

/* Links in assistant responses */
a {
    color: #240F6E;
    font-weight: 600;
}

/* Title */
div[data-testid="stAppViewBlockContainer"] h1 {
    color: #240F6E;
}

/* Caption */
div[data-testid="stCaptionContainer"] p {
    color: #503F8B;
    font-family: 'Open Sans', Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Kaplan Media Consultant")
st.caption("Tell me what you're working on and I'll point you to the right tool.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What do you need help with?"):
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
