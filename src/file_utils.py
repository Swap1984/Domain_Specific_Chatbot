# file_utils.py
import pdfplumber
import docx

def read_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def read_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def load_file(path):
    if path.endswith(".pdf"):
        return read_pdf(path)
    elif path.endswith(".docx"):
        return read_docx(path)
    elif path.endswith(".txt"):
        return read_txt(path)
    else:
        return ""
