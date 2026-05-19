"""Generate the markdown daily intelligence brief."""

from __future__ import annotations

from datetime import datetime

from summarize import summarize_article


SECTION_ORDER = [
    ("🌍 World Essentials", "World Essentials"),
    ("🇮🇳 India", "India"),
    ("🇧🇹 Bhutan", "Bhutan"),
    ("🤖 AI/ML", "AI/ML"),
    ("🧠 Psychology", "Psychology"),
    ("🔬 Discovery Feed", "Discovery Feed"),
]

MAX_ITEMS_BY_SECTION = {
    "World Essentials": 5,
    "India": 3,
    "Bhutan": 3,
    "AI/ML": 5,
    "Psychology": 3,
    "Discovery Feed": 3,
}

SIGNAL_WORDS = [
    "first",
    "new",
    "rising",
    "surge",
    "shift",
    "launch",
    "breakthrough",
    "policy",
    "trend",
    "record",
]

CURIOUS_WORDS = [
    "mystery",
    "ancient",
    "weird",
    "strange",
    "rare",
    "surprising",
    "discovered",
    "unknown",
]

DEEP_READ_SOURCES = {
    "MIT Technology Review AI",
    "Nature News",
    "Hugging Face Blog",
    "OpenAI Blog",
}

WILDCARD_SECTIONS = {
    "Discovery Feed",
    "Psychology",
    "Bhutan",
}


def generate_markdown(
    grouped: dict[str, list[dict[str, str]]],
    errors: list[str] | None = None,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# Daily Intelligence Brief - {today}",
        "",
        "Estimated reading time: under 10 minutes",
        "",
        "## Executive Summary",
        "",
        build_executive_summary(grouped),
        "",
    ]

    for display_title, key in SECTION_ORDER:
        lines.extend(render_section(display_title, grouped.get(key, [])))

    all_articles = flatten(grouped)
    lines.extend(render_emerging_signals(all_articles))
    lines.extend(render_horizon_expander(all_articles))
    lines.extend(render_curiosity_capsule(all_articles))

    return "\n".join(lines).strip() + "\n"


def render_section(title: str, articles: list[dict[str, str]]) -> list[str]:
    lines = [f"## {title}", ""]

    if not articles:
        lines.extend(["No strong RSS items found for this section today.", ""])
        return lines

    section_key = title_without_icon(title)
    limit = MAX_ITEMS_BY_SECTION.get(section_key, 3)

    for article in articles[:limit]:
        lines.append(render_article(article))

    lines.append("")
    return lines


def render_article(article: dict[str, str]) -> str:
    importance = article.get("importance", "Interesting")
    title = article.get("title", "Untitled")
    source = article.get("source", "Source")
    link = article.get("link", "")
    summary = article.get("short_summary") or summarize_article(article)
    return f"- **{importance}**: [{title}]({link}) - {summary} _{source}_"


def render_emerging_signals(articles: list[dict[str, str]]) -> list[str]:
    lines = ["## 📈 Emerging Signals", ""]
    signals = [
        article
        for article in articles
        if any(word in article_text(article) for word in SIGNAL_WORDS)
    ]

    if not signals:
        lines.append("- No clear emerging signal found in today's RSS set.")
    else:
        for article in signals[:3]:
            lines.append(
                f"- **{article.get('importance', 'Interesting')}**: {article['title']} may be worth tracking. "
                f"Track whether follow-up coverage, policy movement, or market/research adoption confirms it."
            )

    lines.append("")
    return lines


def render_horizon_expander(articles: list[dict[str, str]]) -> list[str]:
    lines = ["## 📚 Horizon Expander", ""]
    picks = choose_horizon_picks(articles)

    if not picks:
        lines.append("- No article recommendations available from today's RSS fetch.")
    else:
        for label, article in picks:
            lines.extend(render_horizon_pick(label, article))

    lines.append("")
    return lines


def choose_horizon_picks(articles: list[dict[str, str]]) -> list[tuple[str, dict[str, str]]]:
    if not articles:
        return []

    picked_links = set()
    picks = []

    quick = choose_quick_read(articles)
    if quick:
        picks.append(("Quick read", quick))
        picked_links.add(quick.get("link"))

    deep = choose_deep_read(articles, picked_links)
    if deep:
        picks.append(("Deep read", deep))
        picked_links.add(deep.get("link"))

    wildcard = choose_wildcard_read(articles, picked_links)
    if wildcard:
        picks.append(("Wildcard", wildcard))

    return picks


def choose_quick_read(articles: list[dict[str, str]]) -> dict[str, str] | None:
    candidates = [
        article
        for article in articles
        if estimated_reading_minutes(article) <= 5
        and article.get("importance") in {"Critical", "Important"}
    ]
    return first_sorted(candidates) or first_sorted(articles)


def choose_deep_read(
    articles: list[dict[str, str]],
    picked_links: set[str],
) -> dict[str, str] | None:
    candidates = [
        article
        for article in articles
        if article.get("link") not in picked_links
        and (
            article.get("source") in DEEP_READ_SOURCES
            or estimated_reading_minutes(article) >= 8
        )
    ]
    return first_sorted(candidates)


def choose_wildcard_read(
    articles: list[dict[str, str]],
    picked_links: set[str],
) -> dict[str, str] | None:
    candidates = [
        article
        for article in articles
        if article.get("link") not in picked_links
        and article.get("section") in WILDCARD_SECTIONS
    ]
    return first_sorted(candidates)


def first_sorted(articles: list[dict[str, str]]) -> dict[str, str] | None:
    if not articles:
        return None
    return sorted(articles, key=lambda item: item.get("score", 0), reverse=True)[0]


def render_horizon_pick(label: str, article: dict[str, str]) -> list[str]:
    title = article.get("title", "Untitled")
    link = article.get("link", "")
    read_time = reading_time_label(label, article)
    why = recommendation_reason(label, article)

    return [
        f"**{label}**",
        "",
        f"- Title: [{title}]({link})",
        f"- Estimated reading time: {read_time}",
        f"- URL: {link}",
        f"- Why recommended: {why}",
        "",
    ]


def reading_time_label(label: str, article: dict[str, str]) -> str:
    if label == "Quick read":
        return "3-5 min"
    if label == "Deep read":
        return "10-20 min"
    return f"{estimated_reading_minutes(article)} min"


def estimated_reading_minutes(article: dict[str, str]) -> int:
    text = f"{article.get('title', '')} {article.get('summary', '')}"
    words = len(text.split())
    rss_minutes = max(1, round(words / 180))

    if article.get("source") in DEEP_READ_SOURCES:
        return max(10, rss_minutes)
    if article.get("section") == "World Essentials":
        return max(4, rss_minutes)
    return max(3, rss_minutes)


def recommendation_reason(label: str, article: dict[str, str]) -> str:
    section = article.get("section", "news")
    importance = article.get("importance", "Interesting").lower()

    if label == "Quick read":
        return f"A concise way to catch a {importance} development in {section} without adding much reading load."
    if label == "Deep read":
        return f"Adds context and second-order implications around a high-signal {section} story."
    return f"Pulls attention outside the usual core feed and may add a useful adjacent mental model."


def render_curiosity_capsule(articles: list[dict[str, str]]) -> list[str]:
    lines = ["## 🧠 Curiosity Capsule", ""]
    curious = [
        article
        for article in articles
        if any(word in article_text(article) for word in CURIOUS_WORDS)
    ]
    pick = curious[0] if curious else (articles[0] if articles else None)

    if not pick:
        lines.append("- No curiosity item available today.")
    else:
        lines.append(render_article(pick))

    lines.append("")
    return lines


def build_executive_summary(grouped: dict[str, list[dict[str, str]]]) -> str:
    top_articles = flatten(grouped)[:3]
    if not top_articles:
        return "No RSS items were fetched, so today's brief could not identify a dominant signal."

    sections = sorted({article.get("section", "news") for article in top_articles})
    return f"Today's highest-signal items cluster around {', '.join(sections)}."


def flatten(grouped: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    articles = []
    for section_articles in grouped.values():
        articles.extend(section_articles)
    return sorted(articles, key=lambda item: item.get("score", 0), reverse=True)


def article_text(article: dict[str, str]) -> str:
    return f"{article.get('title', '')} {article.get('summary', '')}".lower()


def title_without_icon(title: str) -> str:
    return " ".join(title.split()[1:])
