# Classplus Mock Extractor Bot

Telegram bot that logs into a Classplus account, lists available mocks, and generates an **offline HTML mock test** (timer, navigation, submit + score analysis) that you can open in any browser.

> ⚠️ **Important:** Classplus APIs differ by setup/vendor. This repo keeps API endpoints configurable via `CLASSPLUS_API_BASE`. You may need to adjust the endpoint paths in `utils.py` to match your environment.

## What’s included

- Pyrogram Telegram bot (`main.py`)
- HTML generator using Jinja2 (`templates/mock_template.html`)
- HTTP client helpers (`utils.py`)
- Optional Flask healthcheck app (`app.py`) for platforms like Render
- Dockerfile + requirements

## Local setup

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure environment

Copy `.env.example` to `.env` and fill values:

```bash
cp .env.example .env
```

Required:

- `API_ID`, `API_HASH` (from Telegram: https://my.telegram.org/apps)
- `BOT_TOKEN` (from @BotFather)

Optional:

- `CLASSPLUS_API_BASE` (your API base URL)
- `TMP_DIR` (where generated HTML will be stored temporarily)

### 3) Run the bot

```bash
python main.py
```

Open Telegram and send:

- `/start`
- `/Cpmock`

Then follow the prompts.

## Docker

```bash
docker build -t classplus-mock-extractor .
docker run --rm -it \
  -e API_ID=... \
  -e API_HASH=... \
  -e BOT_TOKEN=... \
  -e CLASSPLUS_API_BASE=... \
  classplus-mock-extractor
```

## Deploy notes

- **Bot process:** run `python main.py`
- **Web process (optional):** run `python app.py` (healthcheck + file serving)

If you deploy to a platform that expects a web server (like Render free web services), use the Flask app and run the bot as a background worker.

## Project structure

```
.
├─ main.py                 # Telegram bot
├─ app.py                  # Optional Flask server
├─ utils.py                # API + HTML generation helpers
├─ config.py               # Environment-based config
├─ templates/
│  └─ mock_template.html   # Offline mock HTML template
├─ requirements.txt
├─ Dockerfile
└─ .env.example
```

## Troubleshooting

- **`Missing required environment variables`**: create `.env` and set `API_ID`, `API_HASH`, `BOT_TOKEN`.
- **HTML page shows nothing / JS error**: ensure the template can serialize JSON; this repo includes a `tojson` Jinja filter and uses `|safe`.
- **API errors / no mocks found**: update `CLASSPLUS_API_BASE` and, if needed, endpoint paths in `utils.py` (`LOGIN_*`, `FETCH_*`).

## License

See `License`.
