import time
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from pyrogram.enums import ParseMode

from utils import (
    request_otp,
    verify_otp,
    use_auth_code,
    fetch_mock_list,
    fetch_mock_details,
    generate_mock_html,
    cleanup_file,
)

from config import API_ID, API_HASH, BOT_TOKEN


# ----------------------------
# BOT INIT
# ----------------------------
app = Client(
    "classplus_mock_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ----------------------------
# STATES
# ----------------------------
STATE_ORG = 1
STATE_METHOD = 2
STATE_PHONE = 3
STATE_OTP = 4
STATE_AUTH = 5
STATE_MOCK = 6


# ----------------------------
# SESSION STORE
# ----------------------------
sessions = {}
SESSION_TIMEOUT = 900  # 15 minutes


# ----------------------------
# HELPERS
# ----------------------------
def get_session(user_id: int):
    session = sessions.get(user_id)

    if not session:
        return None

    # expire session
    if time.time() - session["ts"] > SESSION_TIMEOUT:
        sessions.pop(user_id, None)
        return None

    session["ts"] = time.time()
    return session


def set_session(user_id: int, data: dict):
    data["ts"] = time.time()
    sessions[user_id] = data


def clean_text(message: Message):
    return (message.text or "").strip()


# ----------------------------
# START
# ----------------------------
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply(
        "👋 Welcome!\nUse /Cpmock to start login."
    )


# ----------------------------
# ENTRY POINT
# ----------------------------
@app.on_message(filters.command("Cpmock"))
async def cpmock(_, message: Message):
    user_id = message.from_user.id

    set_session(user_id, {
        "state": STATE_ORG
    })

    await message.reply(
        "🏢 Enter Organisation Code:"
    )


# ----------------------------
# MAIN HANDLER
# ----------------------------
@app.on_message(filters.private & ~filters.command(["start", "Cpmock"]))
async def handler(_, message: Message):
    user_id = message.from_user.id
    text = clean_text(message)

    session = get_session(user_id)

    if not session:
        await message.reply("⚠️ Session expired. Use /Cpmock again.")
        return

    state = session["state"]

    # ----------------------------
    # STEP 1: ORG CODE
    # ----------------------------
    if state == STATE_ORG:
        session["org_code"] = text
        session["state"] = STATE_METHOD

        set_session(user_id, session)

        keyboard = ReplyKeyboardMarkup(
            [
                [KeyboardButton("OTP Login")],
                [KeyboardButton("Direct Auth Code")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.reply(
            "Choose login method:",
            reply_markup=keyboard
        )
        return

    # ----------------------------
    # STEP 2: METHOD SELECTION
    # ----------------------------
    if state == STATE_METHOD:

        if text.lower() == "otp login":
            session["state"] = STATE_PHONE
            set_session(user_id, session)

            await message.reply("📱 Enter your phone number:")
            return

        if text.lower() == "direct auth code":
            session["state"] = STATE_AUTH
            set_session(user_id, session)

            await message.reply("🔑 Send your Auth Code:")
            return

        await message.reply("⚠️ Choose a valid option.")
        return

    # ----------------------------
    # STEP 3A: PHONE (OTP FLOW)
    # ----------------------------
    if state == STATE_PHONE:
        session["phone"] = text

        try:
            await request_otp(session["phone"], session["org_code"])
        except Exception as e:
            await message.reply(f"❌ OTP request failed:\n{e}")
            return

        session["state"] = STATE_OTP
        set_session(user_id, session)

        await message.reply("📩 OTP sent. Enter OTP:")
        return

    # ----------------------------
    # STEP 3B: OTP VERIFY
    # ----------------------------
    if state == STATE_OTP:
        try:
            token = await verify_otp(
                session["phone"],
                text,
                session["org_code"]
            )
        except Exception as e:
            await message.reply(f"❌ Invalid OTP:\n{e}")
            return

        session["auth_token"] = token
        session["state"] = STATE_MOCK
        set_session(user_id, session)

        await load_mocks(message, session)
        return

    # ----------------------------
    # STEP 3C: DIRECT AUTH CODE
    # ----------------------------
    if state == STATE_AUTH:
        token = use_auth_code(text)

        session["auth_token"] = token
        session["state"] = STATE_MOCK
        set_session(user_id, session)

        await load_mocks(message, session)
        return

    # ----------------------------
    # STEP 4: MOCK SELECTION
    # ----------------------------
    if state == STATE_MOCK:
        mocks = session.get("mocks", [])

        if not any(str(m.get("id")) == text for m in mocks):
            await message.reply("⚠️ Invalid Mock ID. Try again.")
            return

        try:
            await message.reply("⏳ Extracting mock...")

            mock_data = await fetch_mock_details(
                session["auth_token"],
                text
            )

            file_path = generate_mock_html(mock_data)

            await message.reply_document(
                file_path,
                caption=f"📘 {mock_data.get('name', 'Mock Test')}"
            )

            cleanup_file(file_path)

        except Exception as e:
            await message.reply(f"❌ Failed:\n{e}")

        sessions.pop(user_id, None)
        return


# ----------------------------
# LOAD MOCKS
# ----------------------------
async def load_mocks(message: Message, session: dict):
    try:
        mocks = await fetch_mock_list(session["auth_token"])
    except Exception as e:
        await message.reply(f"❌ Failed to load mocks:\n{e}")
        sessions.pop(message.from_user.id, None)
        return

    if not mocks:
        await message.reply("⚠️ No mocks found.")
        sessions.pop(message.from_user.id, None)
        return

    session["mocks"] = mocks
    set_session(message.from_user.id, session)

    text = "📚 Available Mock Tests:\n\n"
    for m in mocks:
        text += f"{m.get('id')} - {m.get('name','Mock')}\n"

    text += "\n👉 Send Mock ID to extract."

    await message.reply(text)


# ----------------------------
# RUN BOT
# ----------------------------
if __name__ == "__main__":
    print("🚀 Bot starting...")
    app.run()
