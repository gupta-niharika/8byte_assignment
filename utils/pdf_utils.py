import spacy, os
import fitz  # PyMuPDF

nlp = spacy.load("en_core_web_sm")

def extract_text_chunks(pdf_path: str, original_filename: str, chunk_size: int=500):
    doc = fitz.open(pdf_path)
    all_chunks = []

    for page_num, page in enumerate(doc):
        doc_spacy = nlp(page.get_text())
        current_chunk = ""

        for sentence in doc_spacy.sents:
            sentence_text = sentence.text
            if len(current_chunk) + len(sentence_text) <= chunk_size:
                current_chunk += " " + sentence_text
            else:
                if current_chunk.strip():
                    all_chunks.append((current_chunk.strip(), f"{original_filename} - page {page_num + 1}"))
                current_chunk = sentence_text

        if current_chunk.strip():
            all_chunks.append((current_chunk.strip(), f"{original_filename} - page {page_num + 1}"))

    return all_chunks
