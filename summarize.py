"""Simple extractive summaries for RSS items."""

from __future__ import annotations

import re


MAX_SUMMARY_CHARS = 220


def summarize_article(article: dict[str, str], max_chars: int = MAX_SUMMARY_CHARS) -> str:
    summary = article.get("summary", "").strip()
    if not summary:
        return "No RSS summary provided."

    first_sentence = split_sentences(summary)[0] if split_sentences(summary) else summary
    return trim_text(first_sentence, max_chars)


def summarize_articles(articles: list[dict[str, str]]) -> list[dict[str, str]]:
    for article in articles:
        article["short_summary"] = summarize_article(article)
    return articles


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    trimmed = text[: max_chars - 3].rsplit(" ", 1)[0]
    return f"{trimmed}..."

