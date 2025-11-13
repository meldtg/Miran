import os
from dotenv import load_dotenv
from os.path import dirname, join, abspath

# Ensure .env is loaded whether we run from repo root or backend dir
_THIS_DIR = dirname(abspath(__file__))
_ROOT_DIR = dirname(_THIS_DIR)
for _candidate in (join(_THIS_DIR, ".env"), join(_ROOT_DIR, ".env")):
    if os.path.exists(_candidate):
        load_dotenv(_candidate, override=False)

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Разрешенные хосты
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Телеграм бот
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Авторизация Mini App
ALLOW_ALL_USERS = os.getenv('ALLOW_ALL_USERS', 'False').lower() == 'true'
_allowed_ids_raw = os.getenv('ALLOWED_USER_IDS', '').strip()
ALLOWED_USER_IDS = []
if _allowed_ids_raw:
    for _id in _allowed_ids_raw.split(','):
        _id = _id.strip()
        if _id.isdigit():
            ALLOWED_USER_IDS.append(int(_id))

# Логи в Telegram
def _parse_int_env(key: str, default: int) -> int:
    try:
        val = os.getenv(key, str(default))
        return int(str(val).strip())
    except Exception:
        return default

LOG_CHAT_ID = _parse_int_env('LOG_CHAT_ID', 3410331288)
LOG_TOPIC_ID = _parse_int_env('LOG_TOPIC_ID', 2)
