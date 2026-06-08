import os
import re
import uuid
import json
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import CLASSPLUS_API_BASE, TMP_DIR


# ----------------------------
# TEMPLATE ENGINE
# ----------------------------
_BASE_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _BASE_DIR / "templates"


def _tojson(value):
    return json.dumps(value, ensure_ascii=False)


env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
)
env.filters["tojson"] = _tojson


# ----------------------------
# API ENDPOINTS (ONLY REAL ONES YOU NEED)
# ----------------------------
OTP_REQUEST_URL = f"{CLASSPLUS_API_BASE}/login/otp/request"
OTP_VERIFY_URL = f"{CLASSPLUS_API_BASE}/login/otp/verify"

FETCH_MOCKS_URL = f"{CLASSPLUS_API_BASE}/mocks"
FETCH_MOCK_DETAIL_URL = f"{CLASSPLUS_API_BASE}/mock"


# ----------------------------
# FILE HANDLING
# ----------------------------
def ensure_tmp_dir():
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)


def _safe_filename(name: str) -> str:
    name = name.strip() or "mock"
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:120]


# =========================================================
# 🔵 OTP LOGIN FLOW (ONLY AUTH METHOD YOU NEED)
# =========================================================

async def request_otp(phone: str, org_code: str):
    """
    Send OTP to user
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OTP_REQUEST_URL, json={
            "phone": phone,
            "org_code": org_code
        })

        if resp.status_code != 200:
            raise Exception(f"OTP request failed: {resp.text}")

        return True


async def verify_otp(phone: str, otp: str, org_code: str):
    """
    Verify OTP and return auth token
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(OTP_VERIFY_URL, json={
            "phone": phone,
            "otp": otp,
            "org_code": org_code
        })

        if resp.status_code != 200:
            raise Exception(f"Invalid OTP: {resp.text}")

        data = resp.json()
        token = data.get("auth_token")

        if not token:
            raise Exception("No auth token received")

        return token


# =========================================================
# 🟢 CORE API FUNCTIONS (KEEP THESE)
# =========================================================

async def fetch_mock_list(auth_token: str):
    async with httpx.AsyncClient(timeout=30) as client:
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get(FETCH_MOCKS_URL, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"Failed to fetch mocks: {resp.text}")

        data = resp.json() if resp.content else {}
        return data.get("mocks", []) or []


async def fetch_mock_details(auth_token: str, mock_id: str):
    async with httpx.AsyncClient(timeout=30) as client:
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get(f"{FETCH_MOCK_DETAIL_URL}/{mock_id}", headers=headers)

        if resp.status_code != 200:
            raise Exception(f"Mock fetch failed: {resp.text}")

        return resp.json()


# =========================================================
# 🟡 HTML GENERATION (KEEP)
# =========================================================

def generate_mock_html(mock_data: dict):
    ensure_tmp_dir()

    template = env.get_template("mock_template.html")

    mock_data = {
        "name": mock_data.get("name", "Mock"),
        "duration_seconds": mock_data.get("duration_seconds", 600),
        "questions": mock_data.get("questions", []),
        **mock_data,
    }

    html_content = template.render(mock=mock_data)

    filename = f"{_safe_filename(mock_data['name'])}_{uuid.uuid4().hex[:8]}.html"
    filepath = os.path.join(TMP_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath


# =========================================================
# 🧹 CLEANUP
# =========================================================

def cleanup_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)
