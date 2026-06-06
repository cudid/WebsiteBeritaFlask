# -*- coding: utf-8 -*-
"""Mesin pencari berita Kompas berbasis TF-IDF & Cosine Similarity."""

import json
import os
import string
from pathlib import Path

import numpy as np
import pandas as pd
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXCEL_PATH = DATA_DIR / "hasil_scraping_kompas.xlsx"
CACHE_PATH = DATA_DIR / "processed_cache.json"


class NewsSearchEngine:
    def __init__(self):
        self.paper = []
        self.processed_paper = []
        self._stopword = StopWordRemoverFactory().create_stop_word_remover()
        self._stemmer = StemmerFactory().create_stemmer()
        self._loaded = False

    def _preprocess_text(self, text: str) -> str:
        text = str(text).lower()
        remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
        text = text.translate(remove_punctuation_map)
        text = self._stopword.remove(text)
        tokens = text.split()
        stemmed_tokens = [self._stemmer.stem(t) for t in tokens]
        return " ".join(stemmed_tokens)

    def _load_from_excel(self):
        if not EXCEL_PATH.exists():
            raise FileNotFoundError(
                f"File data tidak ditemukan: {EXCEL_PATH}\n"
                "Letakkan hasil_scraping_kompas.xlsx di folder data/"
            )
        paper_x = pd.read_excel(EXCEL_PATH)
        self.paper = paper_x.values.tolist()
        self.processed_paper = []
        for row in self.paper:
            text_gabungan = str(row[1]) + " " + str(row[3])
            self.processed_paper.append(self._preprocess_text(text_gabungan))

    def _load_from_cache(self):
        with open(CACHE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        self.paper = data["paper"]
        self.processed_paper = data["processed_paper"]

    def save_cache(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(
                {"paper": self.paper, "processed_paper": self.processed_paper},
                f,
                ensure_ascii=False,
            )

    def load(self):
        if self._loaded:
            return

        if CACHE_PATH.exists():
            self._load_from_cache()
        else:
            self._load_from_excel()
            try:
                self.save_cache()
            except OSError:
                pass

        self._loaded = True

    def search(self, query_input: str, top_n: int = 10):
        self.load()

        query = self._preprocess_text(query_input)
        if not query.strip():
            return []

        vectorizer = TfidfVectorizer(use_idf=True)
        corpus = [query] + self.processed_paper
        paper_tfidf = vectorizer.fit_transform(corpus)
        query_vector = paper_tfidf[0]
        similarity_scores = cosine_similarity(paper_tfidf, query_vector)

        results = []
        for doc_idx in range(1, len(similarity_scores)):
            score = float(similarity_scores[doc_idx][0])
            if score > 0:
                i = doc_idx - 1
                results.append({
                    "document_id": i,
                    "score": round(score, 4),
                    "judul": str(self.paper[i][1]),
                    "waktu": str(self.paper[i][2]),
                    "konten": str(self.paper[i][3]),
                    "url": str(self.paper[i][0]) if len(self.paper[i]) > 0 else "",
                })

        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return results[:top_n]

    @property
    def total_articles(self) -> int:
        self.load()
        return len(self.paper)

    @property
    def is_ready(self) -> bool:
        return CACHE_PATH.exists() or EXCEL_PATH.exists()


_engine = None


def get_engine() -> NewsSearchEngine:
    global _engine
    if _engine is None:
        _engine = NewsSearchEngine()
    return _engine
