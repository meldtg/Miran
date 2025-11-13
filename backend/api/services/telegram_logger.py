import datetime as _dt
import requests
from config import BOT_TOKEN, LOG_CHAT_ID, LOG_TOPIC_ID


def _format_now_utc() -> str:
    return _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def send_user_verified_log(user_data: dict, full_name: str) -> None:
    """
    Sends a verification log to the configured Telegram chat/topic.
    Does not raise on failure.
    """
    try:
        username = user_data.get("username") or ""
        date_str = _format_now_utc()
        text = (
            f"✅ Пользователь прошёл верификацию\n"
            f"Дата: {date_str}\n"
            f"ФИО: {full_name or '—'}\n"
            f"username: @{username}" if username else
            f"✅ Пользователь прошёл верификацию\n"
            f"Дата: {date_str}\n"
            f"ФИО: {full_name or '—'}"
        )
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": LOG_CHAT_ID,
            "message_thread_id": LOG_TOPIC_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        requests.post(url, json=payload, timeout=5)
    except Exception:
        # Best-effort logging; never break the request flow
        pass


