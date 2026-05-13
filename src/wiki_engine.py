from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable
import math
import re

import numpy as np
import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "stardew_wiki_seed.csv"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL_NAME = "google/flan-t5-small"
STOP_WORDS = {
    "about",
    "after",
    "before",
    "best",
    "can",
    "could",
    "does",
    "for",
    "from",
    "give",
    "have",
    "how",
    "into",
    "should",
    "the",
    "this",
    "use",
    "what",
    "when",
    "where",
    "which",
    "with",
}


@dataclass(frozen=True)
class SearchResult:
    title: str
    category: str
    content: str
    source_url: str
    score: float


def load_wiki_data(path: Path = DATA_PATH) -> pd.DataFrame:
    data = pd.read_csv(path)
    required_columns = {"title", "category", "tags", "content", "source_url"}
    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns in wiki data: {sorted(missing)}")

    data = data.fillna("")
    data["search_text"] = (
        data["title"].astype(str)
        + ". Category: "
        + data["category"].astype(str)
        + ". Tags: "
        + data["tags"].astype(str)
        + ". "
        + data["content"].astype(str)
    )
    return data


class WikiSearchEngine:
    """Small semantic search wrapper with a TF-IDF fallback for deployment safety."""

    def __init__(self, data: pd.DataFrame):
        self.data = data.reset_index(drop=True)
        self.mode = "tfidf"
        self._sentence_model = None
        self._embeddings = None
        self._tfidf_vectorizer = None
        self._tfidf_matrix = None
        self._basic_index = None
        self._build_index()

    def _build_index(self) -> None:
        texts = self.data["search_text"].tolist()
        try:
            from sentence_transformers import SentenceTransformer

            self._sentence_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            self._embeddings = self._sentence_model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            self.mode = "huggingface"
        except Exception:
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer

                self._tfidf_vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
                self._tfidf_matrix = self._tfidf_vectorizer.fit_transform(texts)
                self.mode = "tfidf"
            except Exception:
                self._basic_index = [self._token_counts(text) for text in texts]
                self.mode = "keyword"

    def search(self, query: str, category: str = "All", top_k: int = 4) -> list[SearchResult]:
        filtered = self.data
        if category != "All":
            filtered = filtered[filtered["category"] == category]

        if filtered.empty:
            return []

        candidate_indices = filtered.index.to_numpy()
        if self.mode == "huggingface" and self._sentence_model is not None:
            query_embedding = self._sentence_model.encode([query], normalize_embeddings=True)[0]
            scores = self._embeddings[candidate_indices] @ query_embedding
        elif self.mode == "tfidf":
            query_vector = self._tfidf_vectorizer.transform([query])
            scores = (self._tfidf_matrix[candidate_indices] @ query_vector.T).toarray().ravel()
        else:
            query_counts = self._token_counts(query)
            scores = np.array(
                [self._cosine(query_counts, self._basic_index[index]) for index in candidate_indices],
                dtype=float,
            )

        scores = scores + np.array(
            [self._metadata_boost(query, self.data.loc[index]) for index in candidate_indices],
            dtype=float,
        )

        ranked_positions = [
            position for position in np.argsort(scores)[::-1] if scores[position] > 1e-9
        ][:top_k]
        if not ranked_positions:
            ranked_positions = list(np.argsort(scores)[::-1][:1])

        results = []
        for position in ranked_positions:
            row_index = int(candidate_indices[position])
            row = self.data.loc[row_index]
            results.append(
                SearchResult(
                    title=row["title"],
                    category=row["category"],
                    content=row["content"],
                    source_url=row["source_url"],
                    score=float(scores[position]),
                )
            )
        return results

    @staticmethod
    def _token_counts(text: str) -> dict[str, int]:
        tokens = re.findall(r"[a-z0-9']+", text.lower())
        counts: dict[str, int] = {}
        for token in tokens:
            if len(token) <= 2 or token in STOP_WORDS:
                continue
            counts[token] = counts.get(token, 0) + 1
        return counts

    @staticmethod
    def _cosine(left: dict[str, int], right: dict[str, int]) -> float:
        if not left or not right:
            return 0.0
        shared = set(left).intersection(right)
        numerator = sum(left[token] * right[token] for token in shared)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    @classmethod
    def _metadata_boost(cls, query: str, row: pd.Series) -> float:
        query_tokens = set(cls._token_counts(query))
        if not query_tokens:
            return 0.0

        title_tokens = set(cls._token_counts(str(row["title"])))
        tag_tokens = set(cls._token_counts(str(row["tags"])))
        category_tokens = set(cls._token_counts(str(row["category"])))

        boost = 0.0
        boost += 0.18 * len(query_tokens.intersection(title_tokens))
        boost += 0.06 * len(query_tokens.intersection(tag_tokens))
        boost += 0.04 * len(query_tokens.intersection(category_tokens))
        return boost


class WikiAnswerGenerator:
    """Optional Hugging Face text generator with a deterministic fallback."""

    def __init__(self):
        self.mode = "template"
        self._pipeline = None
        self._build_generator()

    def _build_generator(self) -> None:
        try:
            from transformers import pipeline

            self._pipeline = pipeline(
                "text2text-generation",
                model=GENERATION_MODEL_NAME,
                max_new_tokens=220,
            )
            self.mode = "huggingface"
        except Exception:
            self.mode = "template"

    def answer(self, question: str, results: Iterable[SearchResult], style: str = "Balanced") -> str:
        results = list(results)
        if not results:
            return build_answer(question, results, style=style)

        if self.mode != "huggingface" or self._pipeline is None:
            return build_answer(question, results, style=style)

        prompt = self._build_prompt(question, results, style)
        try:
            response = self._pipeline(prompt)[0]["generated_text"].strip()
        except Exception:
            return build_answer(question, results, style=style)

        if not response:
            return build_answer(question, results, style=style)

        sources = ", ".join(result.title for result in results[:3])
        return f"{response}\n\n**Sources used:** {sources}"

    @staticmethod
    def _build_prompt(question: str, results: list[SearchResult], style: str) -> str:
        context = "\n".join(
            f"{index + 1}. {result.title} ({result.category}): {result.content}"
            for index, result in enumerate(results[:5])
        )
        style_instruction = {
            "Quick tip": "Answer in 2 short sentences.",
            "Step-by-step": "Answer as a short numbered plan.",
            "Balanced": "Answer in one helpful paragraph.",
        }.get(style, "Answer in one helpful paragraph.")

        return (
            "You are a game wiki assistant. Use only the provided wiki context. "
            "If the context is incomplete, say what is missing. "
            f"{style_instruction}\n\n"
            f"Question: {question}\n\n"
            f"Wiki context:\n{context}\n\n"
            "Answer:"
        )


def build_answer(question: str, results: Iterable[SearchResult], style: str = "Balanced") -> str:
    results = list(results)
    if not results:
        return "I could not find a strong match in the current wiki dataset. Try a broader question or add more wiki rows to the CSV."

    lead = results[0]
    context_titles = ", ".join(result.title for result in results[:3])

    if style == "Quick tip":
        return (
            f"Best match: {lead.title}. {lead.content} "
            f"Useful related entries: {context_titles}."
        )

    if style == "Step-by-step":
        steps = [
            f"Start with **{lead.title}** because it is the closest wiki match.",
            lead.content,
        ]
        if len(results) > 1:
            steps.append(
                "Then compare the related entries: "
                + "; ".join(f"{item.title} ({item.category})" for item in results[1:4])
                + "."
            )
        steps.append("Use the source snippets below to check the exact wiki context before acting in-game.")
        return "\n\n".join(f"{index + 1}. {step}" for index, step in enumerate(steps))

    return (
        f"Based on the current wiki dataset, the strongest answer is **{lead.title}**.\n\n"
        f"{lead.content}\n\n"
        f"I also found related context from: {context_titles}. "
        "The answer is generated from the local dataset instead of the model's memory, so expanding the CSV will make the assistant more useful."
    )


@lru_cache(maxsize=1)
def get_engine() -> WikiSearchEngine:
    return WikiSearchEngine(load_wiki_data())


@lru_cache(maxsize=1)
def get_generator() -> WikiAnswerGenerator:
    return WikiAnswerGenerator()
