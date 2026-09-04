import json
from itertools import pairwise
from statistics import median
from urllib.parse import urlencode
from urllib.request import urlopen

from szpont_news.configuration import RadarConfiguration
from szpont_news.models import MarketMove

OKX_API_BASE_URL = "https://www.okx.com"
FOUR_HOUR_BAR = "4H"
CONFIRMED_CANDLE_VALUE = "1"
OKX_TIMEOUT_SECONDS = 15


class OkxMarketClient:
    def __init__(self, base_url: str = OKX_API_BASE_URL) -> None:
        self._base_url = base_url.rstrip("/")

    def get_four_hour_market_move(
        self,
        instrument_id: str,
        configuration: RadarConfiguration | None = None,
    ) -> MarketMove:
        selected_configuration = configuration or RadarConfiguration()
        query = urlencode(
            {
                "instId": instrument_id,
                "bar": FOUR_HOUR_BAR,
                "limit": str(selected_configuration.okx_candle_limit),
            }
        )
        payload = self._get_json(f"/api/v5/market/candles?{query}")
        closed_candles = [
            row for row in payload["data"] if row[-1] == CONFIRMED_CANDLE_VALUE
        ]
        closes = [float(row[4]) for row in reversed(closed_candles)]
        if len(closes) < 3:
            raise ValueError("OKX returned insufficient closed 4H candles")
        returns = [
            current / previous - 1 for previous, current in pairwise(closes)
        ]
        typical_sample = returns[:-1][
            -selected_configuration.typical_return_sample_size :
        ]
        return MarketMove(
            instrument_id=instrument_id,
            last_price=closes[-1],
            four_hour_return=returns[-1],
            typical_absolute_four_hour_return=median(map(abs, typical_sample)),
        )

    def _get_json(self, path: str) -> dict[str, object]:
        with urlopen(
            f"{self._base_url}{path}", timeout=OKX_TIMEOUT_SECONDS
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload.get("code") != "0":
            raise RuntimeError(f"OKX request failed: {payload.get('msg', 'unknown error')}")
        return payload
