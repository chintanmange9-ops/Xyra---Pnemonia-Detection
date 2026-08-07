"""ingest_vector_db.py — builds the PDF-based FAISS knowledge store.

Usage:
    python ingest_vector_db.py --pdf_dir <folder_of_pdfs>

Output (default: backend/knowledge/pdf_store/):
    faiss.index    -> cosine-similarity FAISS index (normalized embeddings)
    chunks.json    -> the text chunks + metadata (source, page, chunk_id)

The RAGAgent prefers this store over the PubMed-seeded index whenever it exists.
Re-run after adding new PDFs.
"""

import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

import config

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
MIN_CHUNK_LEN = 40


def extract_text_by_page(pdf_path: str):
    reader = PdfReader(pdf_path)
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            yield page_num, text


def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def build_index(pdf_dir: str, out_dir: str):
    pdf_dir = Path(pdf_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {pdf_dir}")

    print(f"Found {len(pdf_files)} PDFs. Loading embedding model '{config.FAISS_EMBEDDING_MODEL}'...")
    embedder = SentenceTransformer(config.FAISS_EMBEDDING_MODEL)

    all_chunks = []
    all_metadata = []

    for pdf_path in pdf_files:
        for page_num, page_text in extract_text_by_page(str(pdf_path)):
            for i, chunk in enumerate(chunk_text(page_text)):
                if len(chunk.strip()) < MIN_CHUNK_LEN:
                    continue
                all_chunks.append(chunk)
                all_metadata.append({
                    "source": pdf_path.name,
                    "page": page_num + 1,
                    "chunk_id": f"{pdf_path.stem}_p{page_num + 1}_c{i}",
                })

    if not all_chunks:
        raise RuntimeError("No usable text extracted from the PDFs")

    print(f"Embedding {len(all_chunks)} chunks...")
    embeddings = embedder.encode(all_chunks, batch_size=64, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(out_dir / "faiss.index"))
    with open(out_dir / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(
            {"chunks": all_chunks, "metadata": all_metadata, "embed_model": config.FAISS_EMBEDDING_MODEL},
            f,
        )

    print(f"Done. Index has {index.ntotal} vectors. Saved to {out_dir}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build PDF-based FAISS knowledge store")
    parser.add_argument("--pdf_dir", required=True, help="Folder containing your medical guideline PDFs")
    parser.add_argument("--out_dir", default=config.PDF_VECTOR_STORE_DIR, help="Where to save the FAISS index")
    args = parser.parse_args()
    build_index(args.pdf_dir, args.out_dir)
