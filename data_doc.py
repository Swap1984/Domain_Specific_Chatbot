# src/app.py
import streamlit as st
import os
from document_chatbot import DocumentChatbot

st.set_page_config(page_title="Domain-Specific Chatbot", page_icon="💬")
st.title("💬 Document-Based Chatbot")
st.write("Chat with documents already present in the project!")

# Initialize chatbot
if "bot" not in st.session_state:
    st.session_state.bot = DocumentChatbot()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Automatically ingest all documents in data folder
data_folder = "../data"
if "data_loaded" not in st.session_state:
    if os.path.exists(data_folder):
        for file_name in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file_name)
            with open(file_path, "rb") as f:
                st.session_state.bot.ingest_document(f)
        st.session_state.data_loaded = True
        st.success("All documents from data/ folder ingested successfully!")

# User input
user_input = st.text_input("Ask a question:")
if user_input:
    response = st.session_state.bot.get_response(user_input)
    st.session_state.messages.append({"user": user_input, "bot": response})

# Display chat history
for msg in st.session_state.messages:
    st.markdown(f"**You:** {msg['user']}")
    st.markdown(f"**Bot:** {msg['bot']}")
