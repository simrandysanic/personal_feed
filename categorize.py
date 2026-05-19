"""Categorize and lightly rank RSS articles."""

from __future__ import annotations


CATEGORY_MAP = {
    "world": "World Essentials",
    "india": "India",
    "bhutan": "Bhutan",
    "ai": "AI/ML",
    "psychology": "Psychology",
    "science": "Discovery Feed",
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

KEYWORDS = {
    "AI/ML": [
        "ai",
        "artificial intelligence",
        "machine learning",
        "model",
        "llm",
        "agent",
        "openai",
        "hugging face",
    ],
    "Psychology": [
        "psychology",
        "mental",
        "behavior",
        "relationship",
        "productivity",
        "cognitive",
        "brain",
    ],
    "Discovery Feed": [
        "science",
        "space",
        "biology",
        "neuroscience",
        "physics",
        "climate",
        "planet",
        "research",
    ],
    "India": ["india", "delhi", "mumbai", "education", "rbi", "parliament"],
    "Bhutan": ["bhutan", "thimphu", "druk", "gelephu"],
    "World Essentials": [
        "war",
        "election",
        "economy",
        "trade",
        "health",
        "summit",
        "security",
    ],
}

CRITICAL_KEYWORDS_BY_SECTION = {
    "World Essentials": [
        "war",
        "wars",
        "invasion",
        "missile",
        "ceasefire",
        "attack",
        "crisis",
        "emergency",
        "earthquake",
        "election",
        "elections",
        "major policy",
        "regulation",
        "sanctions",
        "inflation",
        "ban",
        "breakthrough",
        "breakthroughs",
        "first-ever",
        "historic",
    ],
    "India": [
        "election",
        "elections",
        "major policy",
        "regulation",
        "ban",
        "crisis",
        "emergency",
    ],
    "Bhutan": [
        "election",
        "elections",
        "major policy",
        "regulation",
        "crisis",
        "emergency",
    ],
    "AI/ML": [
        "breakthrough",
        "breakthroughs",
        "state of the art",
        "major technology",
        "new model",
    ],
    "Discovery Feed": [
        "breakthrough",
        "breakthroughs",
        "first-ever",
        "record",
        "transform",
        "collapses",
        "telescope",
    ],
    "Psychology": [],
}

IMPORTANT_KEYWORDS = [
        "policy",
        "industry",
        "launch",
        "research",
        "findings",
        "economy",
        "education",
        "health",
        "climate",
        "technology",
        "model",
        "national",
        "government",
        "court",
        "funding",
        "partnership",
]

CLICKBAIT_TERMS = [
    "shocking",
    "you won't believe",
    "viral",
    "watch",
]

IMPORTANCE_SCORE = {
    "Critical": 30,
    "Important": 18,
    "Interesting": 8,
}


def categorize_articles(articles: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped = {section: [] for section in CATEGORY_MAP.values()}

    for article in articles:
        section = choose_section(article)
        article["section"] = section
        article["importance"] = choose_importance(article)
        article["score"] = score_article(article)
        grouped.setdefault(section, []).append(article)

    for section_articles in grouped.values():
        section_articles.sort(key=lambda item: item["score"], reverse=True)

    return grouped


def choose_section(article: dict[str, str]) -> str:
    source_category = article.get("source_category", "")
    if source_category in CATEGORY_MAP:
        return CATEGORY_MAP[source_category]

    text = article_text(article)
    best_section = "World Essentials"
    best_score = 0

    for section, keywords in KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > best_score:
            best_section = section
            best_score = score

    return best_section


def choose_importance(article: dict[str, str]) -> str:
    text = article_text(article)
    section = article.get("section", "World Essentials")
    critical_keywords = CRITICAL_KEYWORDS_BY_SECTION.get(section, [])

    if any(contains_keyword(text, keyword) for keyword in critical_keywords):
        return "Critical"

    if any(contains_keyword(text, keyword) for keyword in IMPORTANT_KEYWORDS):
        return "Important"

    return "Interesting"


def score_article(article: dict[str, str]) -> int:
    text = article_text(article)
    title = article.get("title", "").lower()
    importance = choose_importance(article)
    score = IMPORTANCE_SCORE[importance]

    for keywords in KEYWORDS.values():
        score += sum(1 for keyword in keywords if contains_keyword(text, keyword))

    score += source_quality(article) // 10

    if any(contains_keyword(title, term) for term in CLICKBAIT_TERMS):
        score -= 12

    if len(article.get("summary", "")) < 40:
        score -= 2

    return score


def source_quality(article: dict[str, str]) -> int:
    return SOURCE_QUALITY.get(article.get("source", ""), 50)


def article_text(article: dict[str, str]) -> str:
    return f"{article.get('title', '')} {article.get('summary', '')}".lower()


def contains_keyword(text: str, keyword: str) -> bool:
    if " " in keyword or "-" in keyword:
        return keyword in text
    return re_search_word(keyword, text)


def re_search_word(word: str, text: str) -> bool:
    import re

    return re.search(rf"\b{re.escape(word)}\b", text) is not None
