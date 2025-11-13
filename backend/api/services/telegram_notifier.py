import requests
from typing import Optional
from config import BOT_TOKEN
from io import BytesIO

API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _send_message(chat_id: int, text: str) -> bool:
    token = (BOT_TOKEN or "").strip()
    if not token or not chat_id:
        return False
    try:
        url = API_BASE.format(token=token, method="sendMessage")
        resp = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


def notify_support_proposal(
    watcher_user_id: Optional[int],
    area_name: str,
    date_iso: str,
    time_str: str,
    proposer_full_name: Optional[str] = None,
) -> None:
    """
    Уведомление сопровождающему об очередном предложении времени.
    """
    if not watcher_user_id:
        return
    proposer = proposer_full_name or "Проверяющий"
    text = (
        f"🕒 Новое предложение времени сопровождения\n"
        f"Участок: <b>{area_name}</b>\n"
        f"Дата: <b>{date_iso}</b>\n"
        f"Время: <b>{time_str}</b>\n"
        f"Инициатор: <b>{proposer}</b>\n\n"
        f"Откройте мини‑приложение, чтобы принять или отклонить."
    )
    _send_message(int(watcher_user_id), text)


def notify_proposal_response(
    proposer_user_id: Optional[int],
    area_name: str,
    date_iso: str,
    time_str: str,
    action: str,  # "accept" | "reject"
    decided_by_full_name: Optional[str] = None,
) -> None:
    """
    Уведомление проверяющему о решении по его предложению.
    """
    if not proposer_user_id:
        return
    actor = decided_by_full_name or "Сопровождающий"
    status = "принято ✅" if action == "accept" else "отклонено ❌"
    text = (
        f"📣 Решение по предложению времени\n"
        f"Участок: <b>{area_name}</b>\n"
        f"Дата: <b>{date_iso}</b>\n"
        f"Время: <b>{time_str}</b>\n"
        f"Статус: <b>{status}</b>\n"
        f"Решил: <b>{actor}</b>"
    )
    _send_message(int(proposer_user_id), text)


def send_excel_report(chat_id: int, filename: str, data: bytes, caption: Optional[str] = None) -> bool:
    """
    Отправляет Excel-файл пользователю в чат.
    """
    token = (BOT_TOKEN or "").strip()
    if not token or not chat_id or not data:
        return False
    try:
        url = API_BASE.format(token=token, method="sendDocument")
        files = {
            "document": (filename, BytesIO(data), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        }
        payload = {"chat_id": chat_id}
        if caption:
            payload["caption"] = caption
        resp = requests.post(url, data=payload, files=files, timeout=20)
        return resp.status_code == 200
    except Exception:
        return False


