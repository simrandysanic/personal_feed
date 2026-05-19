"""Run the daily intelligence pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from categorize import categorize_articles
from fetch_news import fetch_all
from generate_html import generate_html
from generate_brief import generate_markdown
from summarize import summarize_articles
from telegram_delivery import send_brief_to_telegram


OUTPUT_FILE = Path("daily_brief.md")
HTML_OUTPUT_FILE = Path("daily_brief.html")


def main() -> None:
    args = parse_args()
    articles, errors = fetch_all()
    summarized = summarize_articles(articles)
    grouped = categorize_articles(summarized)
    markdown = generate_markdown(grouped, errors)
    html = generate_html(grouped)
    OUTPUT_FILE.write_text(markdown, encoding="utf-8")
    HTML_OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Wrote {OUTPUT_FILE} with {len(articles)} articles.")
    print(f"Wrote {HTML_OUTPUT_FILE}.")
    if errors:
        print("Some feeds had issues:")
        for error in errors:
            print(f"- {error}")

    if args.send_telegram:
        send_brief_to_telegram(HTML_OUTPUT_FILE)
        print("Sent daily brief to Telegram.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the daily intelligence brief.")
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send daily_brief.md to Telegram after generation.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
