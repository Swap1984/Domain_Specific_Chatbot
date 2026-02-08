# app.py
import os
import streamlit as st
from document_chatbot import DocumentChatbot
from file_utils import load_file

st.set_page_config(page_title="Document Based Chatbot", layout="wide")
st.title(" Document Chatbot (Offline)")

if "bot" not in st.session_state:
    st.session_state.bot = DocumentChatbot()

bot = st.session_state.bot

# Sidebar
st.sidebar.header("Load Documents")

data_dir = "data"
selected_file = None

if os.path.exists(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith((".pdf", ".txt", ".docx"))]
    if files:
        selected_file = st.sidebar.selectbox("Select from data folder", files)

uploaded_file = st.sidebar.file_uploader("Upload a document", type=["pdf", "txt", "docx"])

st.sidebar.subheader("Retrieval Settings")
top_k = st.sidebar.slider("Top-k chunks", min_value=1, max_value=8, value=3)
max_sentences = st.sidebar.slider("Max sentences in answer", min_value=1, max_value=5, value=3)
min_score = st.sidebar.slider("Min relevance score", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
show_chunks = st.sidebar.checkbox("Show retrieved chunks", value=False)

if st.sidebar.button("Load Document"):
    if uploaded_file:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        text = load_file(temp_path)
        os.remove(temp_path)
        msg = bot.ingest_document(text)
        st.sidebar.success(f"Uploaded document loaded. {msg}")
    elif selected_file:
        path = os.path.join(data_dir, selected_file)
        text = load_file(path)
        msg = bot.ingest_document(text)
        st.sidebar.success(f"Loaded `{selected_file}`. {msg}")
    else:
        st.sidebar.warning("Please select or upload a document.")

# Reset
if st.sidebar.button("Reset Bot"):
    bot.text_chunks = []
    bot.embeddings = None
    bot.last_doc_id = None
    st.sidebar.info("Bot state has been reset.")

# Chat interface
st.subheader("Ask Questions")
question = st.text_input("Enter your question")
if st.button("Ask"):
    if not bot.text_chunks:
        st.warning("Please load a document first.")
    elif question.strip():
        results = bot.retrieve(question, top_k=top_k)
        answer = bot.answer(
            question,
            top_k=top_k,
            max_sentences=max_sentences,
            min_score=min_score
        )
        st.markdown("### Answer")
        st.write(answer)

        if show_chunks and results:
            st.markdown("### Retrieved Chunks")
            for rank, (idx, score, chunk) in enumerate(results, start=1):
                with st.expander(f"Chunk {rank} (score {score:.3f})"):
                    st.write(chunk)
    else:
        st.warning("Please enter a question.")
