import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TELEGRAM_API_BASE_URL = "https://api.telegram.org"
TELEGRAM_TIMEOUT_SECONDS = 15


def send_telegram_message(message: str) -> None:
    bot_token = _required_environment_variable("SZPONT_TELEGRAM_BOT_TOKEN")
    chat_id = _required_environment_variable("SZPONT_TELEGRAM_CHAT_ID")
    request = Request(
        f"{TELEGRAM_API_BASE_URL}/bot{bot_token}/sendMessage",
        data=urlencode({"chat_id": chat_id, "text": message}).encode("utf-8"),
        method="POST",
    )
    with urlopen(request, timeout=TELEGRAM_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError("Telegram rejected the notification")


def _required_environment_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing environment variable: {name}")
    return value
