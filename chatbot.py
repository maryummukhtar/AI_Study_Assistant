import streamlit as st
from openai import APIError
from AI_client import create_history, get_study_response


# -----------------------------------
# 1. Page configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("AI Study Assistant")
st.caption(
    "Your learning companion for explanations, summaries, "
    "and practice questions."
)


# -----------------------------------
# 2. Initialize conversation state
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = create_history()


# -----------------------------------
# 3. Sidebar
# -----------------------------------

with st.sidebar:
    st.header("Study Assistant")
    st.write("What would you like to learn today?")

    st.divider()

    st.subheader("Available features")
    st.write("- Explain concepts")
    st.write("- Summarize text")
    st.write("- Generate practice questions")

    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = create_history()
        st.rerun()


# -----------------------------------
# 4. Display previous chat messages
# -----------------------------------

for message in st.session_state.messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------
# 5. Accept a new question
# -----------------------------------

prompt = st.chat_input("Ask a study question...")

if prompt:
    # Display the user's question immediately.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare conversation history for the API.
    next_messages = st.session_state.messages + [
        {"role": "user", "content": prompt}
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_study_response(next_messages)

            st.markdown(answer)

        # Save history only after a successful response.
        st.session_state.messages = next_messages + [
            {"role": "assistant", "content": answer}
        ]

    except (APIError, ValueError) as error:
        st.error(
            "Could not get an answer. Check your API configuration "
            "and connection, then try again."
        )
        print(f"AI API error: {error}")
