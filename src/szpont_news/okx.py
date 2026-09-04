import json
from urllib.parse import urlencode
from urllib.request import urlopen

from szpont_news.models import MarketPrice

OKX_API_BASE_URL = "https://www.okx.com"
OKX_TIMEOUT_SECONDS = 15


class OkxMarketClient:
    def __init__(self, base_url: str = OKX_API_BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")

    def get_market_price(self, instrument_id: str) -> MarketPrice:
        query = urlencode({"instId": instrument_id})
        payload = self._get_json(f"/api/v5/market/ticker?{query}")
        records = payload.get("data", [])
        if len(records) != 1:
            raise ValueError("OKX ticker response must contain exactly one record")
        ticker = records[0]
        last_price = float(ticker["last"])
        open_price = float(ticker["open24h"])
        twenty_four_hour_change = (
            last_price / open_price - 1 if open_price != 0 else None
        )
        return MarketPrice(
            instrument_id=instrument_id,
            last_price=last_price,
            twenty_four_hour_change=twenty_four_hour_change,
        )

    def _get_json(self, path: str) -> dict[str, object]:
        with urlopen(
            f"{self._base_url}{path}", timeout=OKX_TIMEOUT_SECONDS
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("code") != "0":
            raise RuntimeError(f"OKX request failed: {payload.get('msg', 'unknown error')}")
        return payload
