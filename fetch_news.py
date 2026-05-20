"""Fetch RSS items for the daily intelligence brief."""

from __future__ import annotations

from datetime import datetime, timezone
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
import html
import re
from typing import Any

import feedparser
import requests


REQUEST_TIMEOUT = 15
MAX_ITEMS_PER_FEED = 8
SKIP_TITLE_PATTERNS = [
    "comments from",
    "find a therapist",
    "health, help, happiness",
    "letters / kuenselonline",
    "test / quiz",
]
TITLE_SUFFIX_PATTERN = re.compile(r"\s[-|]\s[^-|]+$")
SIMILAR_TITLE_THRESHOLD = 0.72
STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "with",
}

SOURCE_QUALITY = {
    "Reuters World": 100,
    "BBC World": 95,
    "Nature News": 92,
    "The Hindu": 90,
    "OpenAI Blog": 88,
    "MIT Technology Review AI": 86,
    "Indian Express": 84,
    "Hugging Face Blog": 82,
    "ScienceDaily": 78,
    "Kuensel": 76,
    "Psychology Today": 68,
}

RSS_FEEDS = [
    {
        "category": "world",
        "source": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
    },
    {
        "category": "world",
        "source": "Reuters World",
        "url": "https://news.google.com/rss/search?q=site%3Areuters.com%2Fworld&hl=en-US&gl=US&ceid=US%3Aen",
    },
    {
        "category": "india",
        "source": "The Hindu",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
    },
    {
        "category": "india",
        "source": "Indian Express",
        "url": "https://indianexpress.com/section/india/feed/",
    },
    {
        "category": "bhutan",
        "source": "Kuensel",
        "url": "https://news.google.com/rss/search?q=site%3Akuenselonline.com&hl=en-US&gl=US&ceid=US%3Aen",
    },
    {
        "category": "ai",
        "source": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
    },
    {
        "category": "ai",
        "source": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
    },
    {
        "category": "ai",
        "source": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    },
    {
        "category": "psychology",
        "source": "Psychology Today",
        "url": "https://news.google.com/rss/search?q=site%3Apsychologytoday.com&hl=en-US&gl=US&ceid=US%3Aen",
    },
    {
        "category": "science",
        "source": "ScienceDaily",
        "url": "https://www.sciencedaily.com/rss/all.xml",
    },
    {
        "category": "science",
        "source": "Nature News",
        "url": "https://www.nature.com/nature.rss",
    },
]


def clean_text(value: str) -> str:
    """Remove basic HTML and normalize whitespace from RSS fields."""
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    decoded = html.unescape(without_tags)
    return re.sub(r"\s+", " ", decoded).strip()


def parse_date(entry: Any) -> str:
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if not value:
            continue
        try:
            return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
        except (TypeError, ValueError, AttributeError):
            continue
    return datetime.now(timezone.utc).isoformat()


def fetch_feed(feed: dict[str, str], limit: int = MAX_ITEMS_PER_FEED) -> list[dict[str, str]]:
    headers = {"User-Agent": "SimranIntelligenceOS/1.0 (+RSS daily brief)"}
    response = requests.get(feed["url"], headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    parsed = feedparser.parse(response.content)
    articles = []

    for entry in parsed.entries[:limit]:
        title = clean_text(entry.get("title", "Untitled"))
        summary = clean_text(entry.get("summary", entry.get("description", "")))
        link = entry.get("link", feed["url"])

        if not title:
            continue

        if should_skip_title(title):
            continue

        articles.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "source": feed["source"],
                "source_category": feed["category"],
                "published": parse_date(entry),
            }
        )

    return articles


def should_skip_title(title: str) -> bool:
    normalized = title.lower()
    return any(pattern in normalized for pattern in SKIP_TITLE_PATTERNS)


def fetch_all(feeds: list[dict[str, str]] | None = None) -> tuple[list[dict[str, str]], list[str]]:
    """Fetch all configured feeds and return articles plus non-fatal errors."""
    articles: list[dict[str, str]] = []
    errors: list[str] = []

    for feed in feeds or RSS_FEEDS:
        try:
            articles.extend(fetch_feed(feed))
        except requests.RequestException as exc:
            errors.append(f"{feed['source']}: {exc}")
        except Exception as exc:
            errors.append(f"{feed['source']}: {type(exc).__name__}: {exc}")

    return dedupe_articles(articles), errors


def dedupe_articles(articles: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []

    for article in articles:
        duplicate_index = find_similar_article_index(article, unique)

        if duplicate_index is None:
            unique.append(article)
            continue

        current = unique[duplicate_index]
        unique[duplicate_index] = choose_better_article(current, article)

    return unique


def find_similar_article_index(
    article: dict[str, str],
    candidates: list[dict[str, str]],
) -> int | None:
    article_title = normalize_title(article["title"])
    article_link = article["link"].split("?")[0]

    for index, candidate in enumerate(candidates):
        candidate_link = candidate["link"].split("?")[0]
        if article_link == candidate_link:
            return index

        candidate_title = normalize_title(candidate["title"])
        if title_similarity(article_title, candidate_title) >= SIMILAR_TITLE_THRESHOLD:
            return index

    return None


def choose_better_article(
    current: dict[str, str],
    incoming: dict[str, str],
) -> dict[str, str]:
    current_quality = source_quality(current)
    incoming_quality = source_quality(incoming)

    if incoming_quality > current_quality:
        return incoming
    if incoming_quality < current_quality:
        return current

    if len(incoming.get("summary", "")) > len(current.get("summary", "")):
        return incoming

    return current


def source_quality(article: dict[str, str]) -> int:
    return SOURCE_QUALITY.get(article.get("source", ""), 50)


def normalize_title(title: str) -> str:
    title = TITLE_SUFFIX_PATTERN.sub("", title.lower())
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    words = [word for word in title.split() if word not in STOPWORDS]
    return " ".join(words)


def title_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0

    left_tokens = set(left.split())
    right_tokens = set(right.split())
    overlap = len(left_tokens & right_tokens) / max(len(left_tokens | right_tokens), 1)
    sequence = SequenceMatcher(None, left, right).ratio()
    return max(overlap, sequence)


if __name__ == "__main__":
    fetched, feed_errors = fetch_all()
    print(f"Fetched {len(fetched)} articles")
    for error in feed_errors:
        print(f"Feed error: {error}")
