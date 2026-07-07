import streamlit as st  # Import Streamlit library for building web app UI
import uuid
import time

from agent import ask_agent  # Import your custom RAG function that generates chatbot responses

st.title("Agentic RAG-Based Smart Faculty Evaluation System")  # Set the title of the Streamlit app


if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize session state to store chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []  # List to store all chat messages (user + assistant)

# Loop through previous messages and display them on the UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):  # role can be 'user' or 'assistant'
        st.write(message["content"])  # Display the message content

# Get user input from chat box
prompt = st.chat_input("Type here")  # Input field at bottom of chat UI

# If user enters a message
if prompt:

    # Save user message into session state
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message in chat UI
    with st.chat_message("user"):
        st.write(prompt)

    start = time.time()

    response, tool_used = ask_agent(st.session_state.session_id, prompt)

    end = time.time()

    response_time = end - start

    # Save assistant response into session state
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    # Display assistant response in chat UI
    # Display assistant response in chat UI
with st.chat_message("assistant"):

    st.markdown(response)

    st.divider()

    st.markdown(f"**🛠 Tool Used:** `{tool_used}`")

    st.markdown(f"**⏱ Response Time:** `{response_time:.2f} seconds`")