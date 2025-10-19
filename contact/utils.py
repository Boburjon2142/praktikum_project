import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import requests
from dotenv import load_dotenv


def _load_env_from_base_dir() -> None:
    """Load .env located next to manage.py (project BASE_DIR)."""
    # Resolve BASE_DIR conservatively: go up until we find manage.py
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        candidate = parent / "manage.py"
        if candidate.exists():
            load_dotenv(dotenv_path=parent / ".env")
            return
    # Fallback to current working directory
    load_dotenv()


def _escape_markdown_v2(text: str) -> str:
    """Escape Telegram MarkdownV2 reserved characters."""
    if not text:
        return ""
    # Telegram MarkdownV2 special chars to escape
    special = "_[]()~`>#+-=|{}.!*"
    out = []
    for ch in text:
        if ch in special:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def _build_message(data: Dict[str, str], ts: Optional[datetime] = None) -> str:
    name = _escape_markdown_v2(data.get("name", ""))
    email = data.get("email", "")  # keep raw inside mailto link
    safe_email_text = _escape_markdown_v2(email)
    message = _escape_markdown_v2(data.get("message", ""))
    ts = ts or datetime.now()
    timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")

    # Build MarkdownV2 text: labels explicitly bolded as requested
    header = "📩 *Yangi aloqa xabari kelib tushdi!*"
    line_name = f"👤 *ism:* {name}"
    line_email = f"✉️ *email:* [{safe_email_text}](mailto:{email})"
    line_msg = f"💬 *xabar:* {message}"
    line_time = f"🕒 *Yuborilgan vaqt:* {_escape_markdown_v2(timestamp)}"
    return f"{header}\n\n{line_name}\n{line_email}\n{line_msg}\n{line_time}"


def send_contact_message(data: Dict[str, str]) -> bool:
    """
    Send a Markdown-formatted Telegram message using Bot API.

    Expects keys: 'name', 'email', 'message' in data.
    Returns True on success, False otherwise.
    """
    _load_env_from_base_dir()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        return False

    text = _build_message(data)

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.ok:
            body = resp.json()
            return bool(body.get("ok"))
        return False
    except requests.RequestException:
        return False
