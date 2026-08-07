import os
import json
import threading
import numpy as np
import requests

import config


class RAGAgent:
    """Module 4a: Hybrid RAG with local FAISS + PubMed online fallback."""

    PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self):
        self.index = None
        self.metadata = []
        self.embedder = None
        self._initialized = False
        self._init_lock = threading.Lock()

    def _load_or_build_index(self):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(config.FAISS_EMBEDDING_MODEL)

            if os.path.exists(config.FAISS_INDEX_PATH):
                self.index = faiss.read_index(config.FAISS_INDEX_PATH)
                with open(config.FAISS_METADATA_PATH, "r") as f:
                    self.metadata = json.load(f)
                print(f"[RAG] Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                self.index = faiss.IndexFlatL2(config.FAISS_DIMENSION)
                self._seed_from_pubmed()
                self._save_index()
                print(f"[RAG] Built new FAISS index with {self.index.ntotal} vectors")

        except ImportError as e:
            print(f"[RAG] Missing dependency: {e}")
            print("[RAG] RAG agent disabled, will use online PubMed only")
        except Exception as e:
            print(f"[RAG] Init error: {e}")

    def _seed_from_pubmed(self, queries=None, max_results_per_query=10):
        """Fetch clinical guidelines from PubMed and build initial index."""
        if queries is None:
            queries = [
                "pneumonia chest X-ray diagnosis guidelines",
                "community acquired pneumonia radiology criteria",
                "bacterial vs viral pneumonia imaging findings",
                "pneumonia severity index clinical recommendations",
                "lung consolidation chest radiograph differential diagnosis",
            ]

        all_texts = []
        for query in queries:
            articles = self._fetch_pubmed(query, max_results=max_results_per_query)
            all_texts.extend(articles)

        if not all_texts:
            print("[RAG] No articles fetched from PubMed, index will be empty")
            return

        assert self.index is not None and self.embedder is not None
        embeddings = self.embedder.encode(all_texts, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)
        self.metadata = [{"text": t, "source": "pubmed"} for t in all_texts]

    def _fetch_pubmed(self, query: str, max_results: int = 10) -> list[str]:
        try:
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
            }
            resp = requests.get(self.PUBMED_SEARCH_URL, params=search_params, timeout=10)
            resp.raise_for_status()
            ids = resp.json().get("esearchresult", {}).get("idlist", [])

            if not ids:
                return []

            fetch_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "xml",
            }
            resp = requests.get(self.PUBMED_FETCH_URL, params=fetch_params, timeout=15)
            resp.raise_for_status()

            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)

            texts = []
            for article in root.findall(".//PubmedArticle"):
                title_el = article.find(".//ArticleTitle")
                abstract_el = article.find(".//AbstractText")
                title = title_el.text if title_el is not None and title_el.text else ""
                abstract = abstract_el.text if abstract_el is not None and abstract_el.text else ""
                if title or abstract:
                    texts.append(f"{title}. {abstract}".strip())

            return texts

        except Exception as e:
            print(f"[RAG] PubMed fetch error: {e}")
            return []

    def _save_index(self):
        try:
            import faiss
            os.makedirs(os.path.dirname(config.FAISS_INDEX_PATH), exist_ok=True)
            assert self.index is not None
            faiss.write_index(self.index, config.FAISS_INDEX_PATH)
            with open(config.FAISS_METADATA_PATH, "w") as f:
                json.dump(self.metadata, f)
        except Exception as e:
            print(f"[RAG] Failed to save index: {e}")

    def run(self, diagnosis_context: str, query_text: str | None = None) -> list[str]:
        if not self._initialized:
            with self._init_lock:
                if not self._initialized:
                    self._load_or_build_index()
                    self._initialized = True

        if query_text is None:
            query_text = diagnosis_context

        local_results = self._search_local(query_text)
        if local_results and len(local_results) > 0:
            return local_results

        print("[RAG] No good local results, falling back to PubMed online")
        online_results = self._fetch_pubmed(query_text, max_results=5)
        return online_results if online_results else ["No relevant clinical guidelines found."]

    def _search_local(self, query: str, top_k: int = 5) -> list[str]:
        if self.index is None or self.index.ntotal == 0 or self.embedder is None:
            return []

        try:
            query_embedding = self.embedder.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")

            distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata) and dist < 1.5:
                    results.append(self.metadata[idx]["text"])

            return results

        except Exception as e:
            print(f"[RAG] Search error: {e}")
            return []
