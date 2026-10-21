
from AI_client import create_history, get_study_response

import os
import json
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, APIError


# -----------------------------------
# 1. API configuration
# -----------------------------------

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

HISTORY_FILE = Path(__file__).resolve().parent / "chat_history.json"


# -----------------------------------
# 2. Local history functions
# -----------------------------------

def create_history():
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful AI Study Assistant. "
                "Explain concepts clearly and step by step. "
                "Summarize text and generate practice questions "
                "when requested. Use simple language and examples."
            ),
        }
    ]


def load_chats():
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return [
                chat for chat in data
                if isinstance(chat, dict)
                and isinstance(chat.get("messages"), list)
                and isinstance(chat.get("id"), str)
            ]

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_chats():
    # Write to a temporary file before replacing the history file.
    temp_file = HISTORY_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(
            st.session_state.chats,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temp_file.replace(HISTORY_FILE)


def create_chat():
    chat = {
        "id": str(uuid.uuid4()),
        "title": "New Conversation",
        "messages": create_history(),
    }

    st.session_state.chats.insert(0, chat)
    st.session_state.active_chat_id = chat["id"]
    save_chats()


def get_active_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.active_chat_id:
            return chat

    return None


# -----------------------------------
# 3. OpenAI response function
# -----------------------------------

def get_study_response(messages):
    if client is None:
        raise ValueError(
            "OPENAI_API_KEY is missing. Check your .env file."
        )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=messages,
    )

    return response.output_text


# -----------------------------------
# 4. Page configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)


# -----------------------------------
# 5. Dark Forest + Sage Green theme
# -----------------------------------

st.markdown("""
<style>
:root {
    --background: #111713;
    --sidebar: #1D2922;
    --card: #202B24;
    --sage: #52796F;
    --sage-hover: #3F6258;
    --forest: #263D35;
    --text: #F0F4EC;
    --muted: #B8C9B9;
    --border: #35483B;
}

/* Main background */
.stApp {
    background: #111713;
    color: #F0F4EC;
}

[data-testid="stAppViewContainer"] {
    background: #111713;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* General text */
.stApp p,
.stApp label,
.stApp .stMarkdown,
.stApp li {
    color: #F0F4EC;
}

h1, h2, h3, h4 {
    color: #F0F4EC !important;
}

/* Header */
.hero {
    background: linear-gradient(135deg, #263D35, #52796F);
    padding: 30px 28px;
    border: 1px solid #435D4D;
    border-radius: 22px;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.20);
}

.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.25rem;
    font-weight: 750;
    margin: 0;
    letter-spacing: -0.8px;
}

.hero p {
    color: #E0EAE0 !important;
    font-size: 1rem;
    line-height: 1.7;
    margin-top: 10px;
    margin-bottom: 0;
}

.hero-icon {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1D2922;
    border-right: 1px solid #35483B;
}

section[data-testid="stSidebar"] > div {
    background: #1D2922;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #E0EAE0 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown {
    color: #B8C9B9;
}

section[data-testid="stSidebar"] hr {
    border-color: #35483B;
}

/* Buttons */
.stButton > button {
    background: #52796F;
    color: #FFFFFF !important;
    border: 1px solid #52796F;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.65rem 1rem;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #3F6258;
    border-color: #8BAE9D;
    color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(0, 0, 0, 0.18);
}

.stButton > button:focus-visible {
    outline: 2px solid #A7C4A5;
    outline-offset: 3px;
}

/* Chat history buttons */
section[data-testid="stSidebar"] .stButton > button {
    text-align: left;
    justify-content: flex-start;
}

/* Feature cards */
.feature-card {
    background: #202B24;
    border: 1px solid #35483B;
    border-radius: 14px;
    padding: 14px;
    margin: 10px 0;
    color: #DCE8DB;
    font-size: 0.92rem;
    line-height: 1.6;
    transition: border-color 0.2s ease;
}

.feature-card:hover {
    border-color: #789987;
}

.feature-card strong {
    color: #B9D5BE;
}

/* Chat message cards */
div[data-testid="stChatMessage"] {
    background: #202B24;
    border: 1px solid #35483B;
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12);
}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li,
div[data-testid="stChatMessage"] .stMarkdown {
    color: #F0F4EC;
}

/* Chat input */
div[data-testid="stChatInput"] {
    background: #202B24;
    border: 1px solid #52796F;
    border-radius: 16px;
}

div[data-testid="stChatInput"] textarea {
    background: #202B24;
    color: #F0F4EC;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #B8C9B9;
}

div[data-testid="stChatInput"]:focus-within {
    border-color: #8BAE9D;
    box-shadow: 0 0 0 2px rgba(82, 121, 111, 0.20);
}

div[data-testid="stChatInput"] button {
    color: #B9D5BE;
}

/* Other input fields */
.stTextInput input,
.stTextArea textarea {
    background: #202B24;
    color: #F0F4EC;
    border-color: #35483B;
    border-radius: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #B8C9B9;
    font-size: 0.85rem;
    margin-top: 35px;
    padding: 15px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #111713;
}

::-webkit-scrollbar-thumb {
    background: #35483B;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #52796F;
}

/* Mobile */
@media (max-width: 640px) {
    .block-container {
        padding-top: 1rem;
    }

    .hero {
        padding: 22px 18px;
        border-radius: 17px;
    }

    .hero h1 {
        font-size: 1.7rem;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# 6. Initialize local chat history
# -----------------------------------

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "active_chat_id" not in st.session_state:
    if st.session_state.chats:
        st.session_state.active_chat_id = (
            st.session_state.chats[0]["id"]
        )
    else:
        create_chat()

# Recover if the active chat is missing.
if get_active_chat() is None:
    if st.session_state.chats:
        st.session_state.active_chat_id = (
            st.session_state.chats[0]["id"]
        )
    else:
        create_chat()


# -----------------------------------
# 7. Header
# -----------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-icon">📚 🌿</div>
    <h1>AI Study Assistant</h1>
    <p>
        Your personal learning companion.<br>
        Understand concepts, summarize notes,
        and practice with confidence.
    </p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------
# 8. Sidebar and local history
# -----------------------------------

with st.sidebar:
    st.markdown("## 🎓 Study Hub")
    st.caption("Your personal AI learning space")

    st.divider()

    if st.button(
        "＋ New Conversation",
        use_container_width=True,
        type="primary",
    ):
        create_chat()
        st.rerun()

    st.markdown("### 🕘 Local Chat History")

    if not st.session_state.chats:
        st.caption("Your previous conversations will appear here.")
    else:
        for chat in st.session_state.chats:
            visible_messages = [
                message for message in chat["messages"]
                if message.get("role") == "user"
            ]

            title = chat.get("title", "New Conversation")
            if len(title) > 27:
                title = title[:27] + "..."

            button_label = f"💬 {title}"

            if chat["id"] == st.session_state.active_chat_id:
                button_label = f"📍 {title}"

            if st.button(
                button_label,
                key=f"chat_{chat['id']}",
                use_container_width=True,
            ):
                st.session_state.active_chat_id = chat["id"]
                st.rerun()

    st.divider()

    st.markdown("### ✨ Available Features")

    st.markdown("""
    <div class="feature-card">
        💡 <strong>Explain Concepts</strong><br>
        Learn difficult topics step by step.
    </div>

    <div class="feature-card">
        📝 <strong>Summarize Notes</strong><br>
        Turn long text into clear key points.
    </div>

    <div class="feature-card">
        🎯 <strong>Practice Questions</strong><br>
        Test your knowledge with practice.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("🌿 Learn. Practice. Grow.")


# -----------------------------------
# 9. Display active conversation
# -----------------------------------

active_chat = get_active_chat()

if active_chat:
    for message in active_chat["messages"]:
        if message["role"] == "system":
            continue

        avatar = (
            "🧑‍🎓"
            if message["role"] == "user"
            else "📚"
        )

        with st.chat_message(
            message["role"],
            avatar=avatar,
        ):
            st.markdown(message["content"])


# -----------------------------------
# 10. Accept a new question
# -----------------------------------

prompt = st.chat_input(
    "💬 Ask a question or explore a topic..."
)

if prompt:
    active_chat = get_active_chat()

    if active_chat:
        # Save the user's question immediately.
        active_chat["messages"].append({
            "role": "user",
            "content": prompt,
        })

        # Use the first question as the chat title.
        if active_chat["title"] == "New Conversation":
            active_chat["title"] = prompt.replace("\n", " ").strip()

        try:
            save_chats()
        except OSError as error:
            st.error("Could not save local chat history.")
            print(f"History save error: {error}")

        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        # Send conversation history to the AI.
        api_messages = [
            message for message in active_chat["messages"]
            if message["role"] in ("system", "user", "assistant")
        ]

        try:
            with st.chat_message("assistant", avatar="📚"):
                with st.spinner("🌿 Preparing your explanation..."):
                    answer = get_study_response(api_messages)

                st.markdown(answer)

            active_chat["messages"].append({
                "role": "assistant",
                "content": answer,
            })

            save_chats()

        except (APIError, ValueError) as error:
            st.error(
                "Unable to generate a response. Check your API "
                "key, configuration, and internet connection."
            )
            print(f"AI API error: {error}")

        except OSError as error:
            st.error(
                "Your answer was generated, but local history "
                "could not be saved."
            )
            print(f"History save error: {error}")

        # Refresh sidebar so the latest title appears.
        st.rerun()


# -----------------------------------
# 11. Footer
# -----------------------------------

st.markdown("""
<div class="footer">
    Made for curious minds 🌿 • Learn. Practice. Grow.
</div>
""", unsafe_allow_html=True)

