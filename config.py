import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def must_get(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"❌ Missing environment variable: {name}")
    return value


# -----------------------
# Telegram (REQUIRED)
# -----------------------
API_ID = int(must_get("API_ID"))
API_HASH = must_get("API_HASH")
BOT_TOKEN = must_get("BOT_TOKEN")


# -----------------------
# API BASE
# -----------------------
CLASSPLUS_API_BASE = must_get("CLASSPLUS_API_BASE")


# -----------------------
# TEMP DIR
# -----------------------
BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = os.getenv("TMP_DIR", str(BASE_DIR / "tmp"))
