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
API_ID = int(must_get("27400172"))
API_HASH = must_get("56d0a75c5f9a9de6beb5452aa63c2d36")
BOT_TOKEN = must_get("8806359824:AAFDIKyp7V2FpzkQgP2w8k_bK5l12yVJ9ws")


# -----------------------
# API BASE
# -----------------------
CLASSPLUS_API_BASE = must_get("CLASSPLUS_API_BASE")


# -----------------------
# TEMP DIR
# -----------------------
BASE_DIR = Path(__file__).resolve().parent
TMP_DIR = os.getenv("TMP_DIR", str(BASE_DIR / "tmp"))
