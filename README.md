# Simran Intelligence OS

A personalized daily intelligence brief designed to fit into less than 10 minutes of reading while preserving signal, context, and curiosity.

## Objective

Generate a concise daily brief every morning across the topics Simran wants to track:

- World Essentials
- India + Bhutan
- AI/ML
- Psychology
- Discovery Feed
- Emerging Signals
- Horizon Expander
- Curiosity Capsule
- Blind Spot Detector

## Editorial Rules

- Total reading time must stay under 10 minutes.
- Avoid clickbait, outrage loops, and low-signal repetition.
- Prefer primary sources, official releases, reputable reporting, and expert analysis.
- Mark each item by importance: `Critical`, `Important`, or `Interesting`.
- Separate confirmed facts from interpretation.
- Include India and Bhutan as first-class context, not as afterthoughts.
- Favor durable developments over noisy daily churn.

## Daily Brief Shape

Use the template in [brief-template.md](brief-template.md).

Each morning brief should include:

1. A one-line executive summary.
2. The nine sections defined in the template.
3. Short source links for each news or research item.
4. A blind spot detector listing areas that were thinly covered or absent.

## Source Strategy

Use [sources.md](sources.md) as the default source map. The source list is intentionally compact: it is better to read fewer reliable sources well than skim a huge feed poorly.

## Generation Prompt

Use [prompts/daily-brief.md](prompts/daily-brief.md) as the operating prompt for the morning automation or for manual generation.

## Local RSS Pipeline

This project includes a simple Python pipeline:

```text
Fetch RSS -> extract title + summary -> categorize -> generate daily_brief.md
```

### Files

- `fetch_news.py`: RSS feed configuration and article extraction
- `categorize.py`: section assignment and simple importance scoring
- `summarize.py`: short extractive summaries from RSS descriptions
- `generate_brief.py`: markdown report generation
- `telegram_delivery.py`: Telegram Bot API delivery
- `main.py`: runs the full pipeline
- `requirements.txt`: Python dependencies

### Run Locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the brief:

```bash
python main.py
```

The reports will be written to:

```text
daily_brief.md
daily_brief.html
```

The pipeline uses free RSS feeds only. Where a publication does not expose a reliable direct RSS endpoint, the project uses a free Google News RSS search scoped to that source.

### Telegram Delivery

Create a Telegram bot with BotFather, then copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

```text
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_VERIFY_SSL=true
```

If your local network or macOS Python install has certificate-chain issues with Telegram, set `TELEGRAM_VERIFY_SSL=false`. Use that only when needed.

Generate and send the brief:

```bash
python main.py --send-telegram
```

The report is sent as a designed HTML document with a minimal beige-and-black newspaper layout. A Markdown copy is still generated for archival or debugging use.

### 7 AM Schedule

For a local machine, add this to cron with `crontab -e`:

```cron
0 7 * * * cd /Users/simran/Documents/simran-intelligence-os && .venv/bin/python main.py --send-telegram
```

Keep the machine awake and connected to the internet at 7 AM.

### GitHub Actions Automation

This repo includes a GitHub Actions workflow at `.github/workflows/daily_brief.yml`.

It runs every day at **7:00 AM India time** and can also be run manually from the GitHub Actions tab.

Before enabling it, add these repository secrets in GitHub:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Optional secret:

```text
TELEGRAM_VERIFY_SSL
```

Use `true` for GitHub Actions unless you have a specific certificate issue. The local `.env` file is not used by GitHub Actions; secrets are injected as environment variables by the workflow.

To add secrets:

1. Open the GitHub repository.
2. Go to `Settings` -> `Secrets and variables` -> `Actions`.
3. Click `New repository secret`.
4. Add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
5. Open `Actions` -> `Daily Intelligence Brief` -> `Run workflow` to test manually.
