import os
from urllib import request, parse


def notify_telegram(text: str) -> None:
    """Send a text message to a Telegram chat using Bot API.

    Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment variables.
    Silently no-ops if configuration is missing.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return  # not configured
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': 'true',
    }
    encoded = parse.urlencode(data).encode('utf-8')
    req = request.Request(api_url, data=encoded)
    # Fail silently — this is a best‑effort notification
    try:
        with request.urlopen(req, timeout=5) as _:
            pass
    except Exception:
        # Ignore network errors to avoid breaking the request flow
        return

