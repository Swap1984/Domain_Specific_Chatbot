# embedding_model.py
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def load_embedding_model():
    """
    Load the embedding model only once and cache it.
    """
    return SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

# Expose a global model for simplicity
MODEL = load_embedding_model()
