# document_chatbot.py
import os
import re
import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embedding_model import MODEL


def normalize_text(text):
    if not text:
        return ""
    # Normalize line endings and whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    # Merge lines that are likely part of the same paragraph
    lines = [ln.strip() for ln in text.split("\n")]
    merged = []
    buffer = ""
    for ln in lines:
        if not ln:
            if buffer:
                merged.append(buffer.strip())
                buffer = ""
            continue

        # If line ends with punctuation, treat as a sentence end
        if re.search(r"[.!?]$", ln):
            buffer = f"{buffer} {ln}".strip()
            merged.append(buffer.strip())
            buffer = ""
        else:
            buffer = f"{buffer} {ln}".strip()

    if buffer:
        merged.append(buffer.strip())

    return "\n".join(merged)


def chunk_text_better(text, max_words=250, overlap_sentences=2):
    text = normalize_text(text)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    cur = []
    cur_words = 0

    def flush_chunk():
        if cur:
            chunks.append(" ".join(cur))

    for p in paragraphs:
        words = p.split()
        if len(words) > max_words:
            sentences = re.split(r"(?<=[.!?]) +", p)
            for s in sentences:
                s_words = s.split()
                if cur_words + len(s_words) > max_words:
                    flush_chunk()
                    cur[:] = cur[-overlap_sentences:]
                    cur_words = sum(len(x.split()) for x in cur)
                cur.append(s)
                cur_words += len(s_words)
        else:
            if cur_words + len(words) > max_words:
                flush_chunk()
                cur[:] = cur[-overlap_sentences:]
                cur_words = sum(len(x.split()) for x in cur)
            cur.append(p)
            cur_words += len(words)

    flush_chunk()
    return chunks


def looks_like_toc(chunk, min_short_lines=6, max_line_len=40, digit_ratio=0.15):
    lines = [ln.strip() for ln in chunk.split("\n") if ln.strip()]
    if not lines:
        return False
    short_lines = sum(1 for ln in lines if len(ln) <= max_line_len)
    digits = sum(ch.isdigit() for ch in chunk)
    ratio = digits / max(1, len(chunk))
    has_toc_keywords = any(
        kw in chunk.lower()
        for kw in ["table of contents", "contents", "chapter", "section", "page"]
    )
    return (short_lines >= min_short_lines and ratio >= digit_ratio) or has_toc_keywords


class DocumentChatbot:
    def __init__(self, cache_dir="models_cache"):
        self.model = MODEL
        self.text_chunks = []
        self.embeddings = None
        self.cache_dir = cache_dir
        self.last_doc_id = None

    def _ensure_cache_dir(self):
        os.makedirs(self.cache_dir, exist_ok=True)

    def _text_hash(self, text):
        return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

    def _cache_path(self, doc_id):
        return os.path.join(self.cache_dir, f"embeddings_{doc_id}.npz")

    def ingest_document(self, text, doc_id=None):
        if not text:
            self.text_chunks = []
            self.embeddings = None
            self.last_doc_id = None
            return "Empty document."

        doc_id = doc_id or self._text_hash(text)
        self.last_doc_id = doc_id
        self._ensure_cache_dir()

        cache_path = self._cache_path(doc_id)
        if os.path.exists(cache_path):
            data = np.load(cache_path, allow_pickle=True)
            self.text_chunks = data["chunks"].tolist()
            self.embeddings = data["embeddings"]
            return "Loaded cached embeddings."

        chunks = chunk_text_better(text)
        chunks = [c for c in chunks if not looks_like_toc(c)]

        self.text_chunks = chunks
        self.embeddings = self.model.encode(
            self.text_chunks,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        np.savez_compressed(
            cache_path,
            chunks=np.array(self.text_chunks, dtype=object),
            embeddings=self.embeddings
        )
        return "Document processed."

    def retrieve(self, question, top_k=3):
        if self.embeddings is None or not self.text_chunks:
            return []

        q_emb = self.model.encode([question], convert_to_numpy=True)
        scores = cosine_similarity(q_emb, self.embeddings)[0]
        top_k = min(top_k, len(self.text_chunks))
        top_idx = np.argsort(scores)[-top_k:][::-1]
        return [(int(i), float(scores[i]), self.text_chunks[i]) for i in top_idx]

    def answer(self, question, top_k=3, max_sentences=3, min_score=0.2):
        results = self.retrieve(question, top_k=top_k)
        if not results:
            return "No document loaded."

        if results[0][1] < min_score:
            return "No relevant information found."

        candidates = []
        for _, _, chunk in results:
            sentences = [
                s.strip()
                for s in re.split(r"(?<=[.!?]) +", chunk)
                if len(s.strip()) > 25
            ]
            candidates.extend(sentences)

        if not candidates:
            return "Relevant information was found, but could not be summarized clearly."

        sent_emb = self.model.encode(
            candidates,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        q_emb = self.model.encode([question], convert_to_numpy=True)
        scores = cosine_similarity(q_emb, sent_emb)[0]
        top_idx = np.argsort(scores)[-max_sentences:][::-1]
        return " ".join([candidates[i] for i in top_idx])
