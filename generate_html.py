"""Generate a minimal newspaper-style HTML daily brief."""

from __future__ import annotations

from datetime import datetime
from html import escape

from generate_brief import (
    CURIOUS_WORDS,
    SECTION_ORDER,
    SIGNAL_WORDS,
    choose_horizon_picks,
)
from summarize import summarize_article


SECTION_LABELS = {
    "World Essentials": "World Essentials",
    "India": "India",
    "Bhutan": "Bhutan",
    "AI/ML": "AI/ML",
    "Psychology": "Psychology",
    "Discovery Feed": "Discovery Feed",
}

MAX_ITEMS_BY_SECTION = {
    "World Essentials": 5,
    "India": 3,
    "Bhutan": 3,
    "AI/ML": 5,
    "Psychology": 3,
    "Discovery Feed": 3,
}


def generate_html(grouped: dict[str, list[dict[str, str]]]) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    sections = "\n".join(render_section(key, grouped.get(key, [])) for _, key in SECTION_ORDER)
    all_articles = flatten(grouped)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Daily Intelligence Brief - {today}</title>
  <style>
    :root {{
      --page: #efe7da;
      --paper: #fffaf1;
      --paper-soft: #f8efe3;
      --ink: #24201c;
      --muted: #7f7469;
      --rule: #b9aa99;
      --soft-rule: #e5d8c8;
      --accent: #9f5d5f;
      --accent-soft: #ead0ca;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: var(--page);
      color: var(--ink);
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.62;
    }}

    main {{
      width: min(1040px, calc(100% - 28px));
      margin: 22px auto;
      background: var(--paper);
      border: 1px solid #eadfce;
      border-radius: 18px;
      box-shadow: 0 22px 70px rgba(57, 42, 29, 0.10);
      padding: 42px clamp(22px, 5vw, 58px) 58px;
    }}

    .masthead {{
      border-bottom: 1px solid var(--soft-rule);
      padding-bottom: 26px;
      text-align: center;
    }}

    .kicker {{
      margin: 0 0 6px;
      color: var(--muted);
      font-family: "Avenir Next", Avenir, Helvetica, Arial, sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      color: #201b18;
      font-size: clamp(38px, 6vw, 68px);
      font-weight: 500;
      line-height: 1;
      letter-spacing: 0;
    }}

    .meta {{
      margin: 14px 0 0;
      color: var(--muted);
      font-family: "Avenir Next", Avenir, Helvetica, Arial, sans-serif;
      font-size: 13px;
    }}

    .summary {{
      width: min(760px, 100%);
      margin: 28px auto 34px;
      color: #3d332c;
      font-size: clamp(18px, 2.4vw, 23px);
      font-style: italic;
      text-align: center;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 30px 34px;
    }}

    section {{
      background: linear-gradient(180deg, rgba(248, 239, 227, 0.68), rgba(255, 250, 241, 0));
      border-top: 1px solid var(--soft-rule);
      border-radius: 14px 14px 0 0;
      padding-top: 14px;
    }}

    section.full {{
      grid-column: 1 / -1;
    }}

    h2 {{
      margin: 0 0 10px;
      color: #3b332d;
      font-family: "Avenir Next", Avenir, Helvetica, Arial, sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }}

    article {{
      border-top: 1px solid var(--soft-rule);
      padding: 14px 0;
    }}

    article:first-of-type {{
      border-top: 0;
      padding-top: 0;
    }}

    h3 {{
      margin: 0 0 6px;
      color: #241f1b;
      font-size: 18px;
      font-weight: 500;
      line-height: 1.24;
    }}

    a {{
      color: var(--ink);
      text-decoration-color: var(--accent);
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}

    .summary-text {{
      margin: 0 0 8px;
      color: #4b4038;
      font-size: 14.5px;
    }}

    .tagline {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-family: "Avenir Next", Avenir, Helvetica, Arial, sans-serif;
      font-size: 11px;
      text-transform: uppercase;
    }}

    .importance {{
      background: var(--accent-soft);
      border-radius: 999px;
      color: #69383b;
      font-weight: 700;
      padding: 2px 7px;
    }}

    .horizon {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }}

    .horizon-card {{
      background: var(--paper-soft);
      border: 1px solid var(--soft-rule);
      border-radius: 14px;
      padding: 16px;
    }}

    .label {{
      margin: 0 0 8px;
      color: var(--accent);
      font-family: "Avenir Next", Avenir, Helvetica, Arial, sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}

    .reason {{
      margin: 8px 0 0;
      color: #4b4038;
      font-size: 14px;
    }}

    @media (max-width: 720px) {{
      main {{
        width: min(100% - 14px, 1040px);
        margin: 7px auto;
        border-radius: 14px;
        padding: 28px 18px 42px;
      }}

      .grid,
      .horizon {{
        grid-template-columns: 1fr;
      }}

      h3 {{
        font-size: 18px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header class="masthead">
      <p class="kicker">Simran Intelligence OS</p>
      <h1>Daily Brief</h1>
      <p class="meta">{today} · Under 10 minutes · Signal over noise</p>
    </header>

    <p class="summary">{escape(build_summary(grouped))}</p>

    <div class="grid">
      {sections}
      {render_html_emerging_signals(all_articles)}
      {render_html_horizon(all_articles)}
      {render_html_curiosity(all_articles)}
    </div>
  </main>
</body>
</html>
"""


def render_section(section_name: str, articles: list[dict[str, str]]) -> str:
    title = SECTION_LABELS.get(section_name, section_name)
    limit = MAX_ITEMS_BY_SECTION.get(section_name, 3)
    body = "\n".join(render_article(article) for article in articles[:limit])

    if not body:
        body = '<p class="summary-text">No strong RSS items found for this section today.</p>'

    return f"""<section>
  <h2>{escape(title)}</h2>
  {body}
</section>"""


def render_article(article: dict[str, str]) -> str:
    title = escape(article.get("title", "Untitled"))
    link = escape(article.get("link", ""))
    source = escape(article.get("source", "Source"))
    importance = escape(article.get("importance", "Interesting"))
    summary = escape(article.get("short_summary") or summarize_article(article))

    return f"""<article>
  <h3><a href="{link}">{title}</a></h3>
  <p class="summary-text">{summary}</p>
  <div class="tagline"><span class="importance">{importance}</span><span>{source}</span></div>
</article>"""


def render_html_emerging_signals(articles: list[dict[str, str]]) -> str:
    signals = [
        article
        for article in articles
        if any(word in article_text(article) for word in SIGNAL_WORDS)
    ][:3]

    body = "\n".join(render_signal(article) for article in signals)
    if not body:
        body = '<p class="summary-text">No clear emerging signal found in today\'s RSS set.</p>'

    return f"""<section class="full">
  <h2>Emerging Signals</h2>
  {body}
</section>"""


def render_signal(article: dict[str, str]) -> str:
    title = escape(article.get("title", "Untitled"))
    importance = escape(article.get("importance", "Interesting"))
    return f"""<article>
  <h3>{title}</h3>
  <p class="summary-text">Track whether follow-up coverage, policy movement, or market adoption confirms it.</p>
  <div class="tagline"><span class="importance">{importance}</span><span>Emerging signal</span></div>
</article>"""


def render_html_horizon(articles: list[dict[str, str]]) -> str:
    picks = choose_horizon_picks(articles)
    if not picks:
        body = '<p class="summary-text">No article recommendations available from today\'s RSS fetch.</p>'
    else:
        body = "\n".join(render_horizon_card(label, article) for label, article in picks)

    return f"""<section class="full">
  <h2>Horizon Expander</h2>
  <div class="horizon">{body}</div>
</section>"""


def render_horizon_card(label: str, article: dict[str, str]) -> str:
    title = escape(article.get("title", "Untitled"))
    link = escape(article.get("link", ""))
    read_time = "10-20 min" if label == "Deep read" else "3-5 min" if label == "Quick read" else "3 min"
    section = escape(article.get("section", "news"))

    if label == "Quick read":
        reason = f"A concise way to catch a high-signal {section} development."
    elif label == "Deep read":
        reason = f"Useful for understanding second-order implications in {section}."
    else:
        reason = "A useful stretch beyond the usual core feed."

    return f"""<div class="horizon-card">
  <p class="label">{escape(label)}</p>
  <h3><a href="{link}">{title}</a></h3>
  <div class="tagline"><span>{read_time}</span></div>
  <p class="reason">{escape(reason)}</p>
</div>"""


def render_html_curiosity(articles: list[dict[str, str]]) -> str:
    curious = [
        article
        for article in articles
        if any(word in article_text(article) for word in CURIOUS_WORDS)
    ]
    pick = curious[0] if curious else (articles[0] if articles else None)
    body = render_article(pick) if pick else ""

    if not body:
        body = '<p class="summary-text">No curiosity item available today.</p>'

    return f"""<section class="full">
  <h2>Curiosity Capsule</h2>
  {body}
</section>"""


def build_summary(grouped: dict[str, list[dict[str, str]]]) -> str:
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
